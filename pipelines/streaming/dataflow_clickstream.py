import json
import logging
import argparse
import datetime
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.transforms.window import SlidingWindows

class ParseAndFilterEvents(beam.DoFn):
    """Parse JSON event and validate mandatory fields."""
    def process(self, element):
        try:
            event = json.loads(element.decode("utf-8"))
            if "user_id" in event and "timestamp" in event:
                # Convert ISO string timestamp or float epoch to seconds for Beam windowing
                ts_str = event["timestamp"]
                # Parse ISO timestamp or handle raw float seconds
                try:
                    ts = datetime.datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp()
                except ValueError:
                    ts = float(ts_str)
                yield beam.window.TimestampedValue(event, ts)
        except Exception as e:
            logging.error(f"Error parsing event: {e}")

def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project_id",
        default="gcp-pde-project-505510",
        help="GCP Project ID to run against"
    )
    parser.add_argument(
        "--subscription",
        default="clickstream-sub",
        help="Pub/Sub subscription name"
    )
    parser.add_argument(
        "--dataset_id",
        default="ecommerce_lakehouse",
        help="BigQuery dataset ID"
    )
    known_args, pipeline_args = parser.parse_known_args(argv)

    options = PipelineOptions(pipeline_args)
    # Always configure streaming mode
    options.view_as(StandardOptions).streaming = True

    sub_path = f"projects/{known_args.project_id}/subscriptions/{known_args.subscription}"
    output_table = f"{known_args.project_id}:{known_args.dataset_id}.realtime_user_activity"

    logging.info(f"Starting pipeline reading from {sub_path} and writing to {output_table}")

    with beam.Pipeline(options=options) as p:
        (
            p
            | "ReadFromPubSub" >> beam.io.ReadFromPubSub(subscription=sub_path)
            | "ParseJSON" >> beam.ParDo(ParseAndFilterEvents())
            # Sliding window 5 minutes (300 seconds), evaluated every 1 minute (60 seconds) with late tolerance of 2 minutes (120 seconds)
            | "SlidingWindow" >> beam.WindowInto(
                SlidingWindows(size=300, period=60),
                allowed_lateness=120
            )
            | "ExtractUserID" >> beam.Map(lambda x: (x["user_id"], 1))
            | "CountPerUser" >> beam.CombinePerKey(sum)
            | "FormatOutput" >> beam.Map(lambda kv: {
                "user_id": kv[0],
                "event_count": int(kv[1]),
                "processed_at": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            })
            | "WriteToBigQuery" >> beam.io.WriteToBigQuery(
                table=output_table,
                schema="user_id:STRING, event_count:INTEGER, processed_at:TIMESTAMP",
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
            )
        )

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()
