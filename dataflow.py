import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.io.gcp.pubsub import ReadFromPubSub, WriteToPubSub
from apache_beam.io.gcp.bigquery import WriteToBigQuery, BigQueryDisposition
from apache_beam import window
from apache_beam.pvalue import TaggedOutput


import json
import time
from datetime import datetime
import logging

# --------------- CONFIGURATION -------------------
PROJECT_ID = 'consummate-fold-466316-c3'
INPUT_TOPIC = f'projects/{PROJECT_ID}/topics/orders-stream'
DLQ_TOPIC = f'projects/{PROJECT_ID}/topics/orders-dlq'
BQ_TABLE = 'consummate-fold-466316-c3.realtime.orders_stream'
TEMP_GCS_BUCKET = 'gs://realtimepra18/temp'
# -------------------------------------------------

class ParseOrderFn(beam.DoFn):
    def process(self, element):
        try:
            record = json.loads(element.decode('utf-8'))
            yield record
        except Exception as e:
            logging.error(f"❌ Bad record: {element} — {e}")
            yield TaggedOutput('DLQ', element)

def add_event_timestamp(element):
    ts = element.get('timestamp')
    try:
        dt = datetime.fromisoformat(ts)
        unix_ts = time.mktime(dt.timetuple())
        return beam.window.TimestampedValue(element, unix_ts)
    except Exception as e:
        logging.error(f"❌ Bad timestamp format: {ts}")
        return beam.window.TimestampedValue(element, time.time())

def run():
    options = PipelineOptions(
        streaming=True,
        project=PROJECT_ID,
        region='us-central1',
        temp_location=TEMP_GCS_BUCKET,
        runner='DataflowRunner'
    )
    p = beam.Pipeline(options=options)

    messages = (
        p
        | "Read from Pub/Sub" >> ReadFromPubSub(topic=INPUT_TOPIC)
        | "Parse and Separate Bad Records" >> beam.ParDo(ParseOrderFn()).with_outputs('DLQ', main='valid')
    )

    valid = (
        messages.valid
        | "Assign Event Timestamps" >> beam.Map(add_event_timestamp)
        | "Hopping Window" >> beam.WindowInto(
            window.SlidingWindows(size=300, period=60),
            allowed_lateness=180,
            accumulation_mode=beam.trigger.AccumulationMode.ACCUMULATING)
    )

    valid | "Write to BigQuery" >> WriteToBigQuery(
        table=BQ_TABLE,
        schema='order_id:STRING, product_id:STRING, timestamp:TIMESTAMP, amount:FLOAT, region:STRING',
        create_disposition=BigQueryDisposition.CREATE_IF_NEEDED,
        write_disposition=BigQueryDisposition.WRITE_APPEND,
        custom_gcs_temp_location=TEMP_GCS_BUCKET
    )

    messages.DLQ | "Send to DLQ Pub/Sub" >> WriteToPubSub(DLQ_TOPIC)

    p.run()

if __name__ == '__main__':
    run()
