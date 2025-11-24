from datetime import datetime, UTC
import http
from os import path

from schemas.client_albert import ConsommationReponse, UneConsommation

DUMMY_PATH = path.join(path.dirname(__file__), "..", "..", "dummy")


def test_peut_deserialiser_les_donnees_d_usage():
    with open(path.join(DUMMY_PATH, "usage.json"), "r") as file:
        payload_usage = file.read()
        usage = ConsommationReponse.model_validate_json(payload_usage)

        assert usage.data[0] == UneConsommation(
            completion_tokens=6.0,
            cost=0.0,
            datetime=datetime(2025, 11, 20, 10, 25, 30, tzinfo=UTC),
            duration=282,
            endpoint="/v1/chat/completions",
            id=18830730,
            model="mistralai/Mistral-Small-3.2-24B-Instruct-2506",
            status=http.HTTPStatus.OK,
            time_to_first_token=None,
            token_id=2818,
            total_tokens=1196,
            user_id=8766,
            kgco2eq_max=0.0,
            kgco2eq_min=0.0,
            kwh_max=0.0,
            kwh_min=0.0,
            method=http.HTTPMethod.POST,
            prompt_tokens=1190,
            request_model="albert-large",
        )
        assert usage.has_more is True
        assert usage.page == 1
