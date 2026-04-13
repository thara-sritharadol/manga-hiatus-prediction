from prefect import task, flow
import time

from jikan_enricher import enrich_with_jikan
from mu_enricher import enrich_with_mangaupdates

@task(retries=5, retry_delay_seconds=60)
def run_jikan_enricher():
    print("--- Starting Jikan Enricher ---")
    enrich_with_jikan()

@task(retries=5, retry_delay_seconds=60)
def run_mu_enricher():
    print("--- Starting MU Enricher (Final Step) ---")
    enrich_with_mangaupdates()

@flow(name="Enricher Pipeline")
def manga_full_pipeline():

    run_jikan_enricher()
    run_mu_enricher()

if __name__ == "__main__":
    manga_full_pipeline()