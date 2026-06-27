"""Tests for the Socrata API client."""

from unittest.mock import MagicMock, patch

from src.ingestion.socrata_client import SocrataClient


class TestSocrataClientInit:
    def test_sets_domain(self):
        client = SocrataClient(domain="data.seattle.gov")
        assert client.domain == "data.seattle.gov"

    def test_sets_app_token_header(self):
        client = SocrataClient(domain="data.seattle.gov", app_token="test-token")
        assert client.session.headers["X-App-Token"] == "test-token"

    def test_no_app_token_header_when_none(self):
        client = SocrataClient(domain="data.seattle.gov")
        assert "X-App-Token" not in client.session.headers


class TestBuildUrl:
    def test_builds_correct_url(self):
        client = SocrataClient(domain="data.seattle.gov")
        url = client._build_url("76t5-zqzr")
        assert url == "https://data.seattle.gov/resource/76t5-zqzr.json"


class TestGetRecords:
    @patch.object(SocrataClient, "_build_url", return_value="https://data.seattle.gov/resource/test.json")
    def test_passes_query_params(self, mock_url):
        client = SocrataClient(domain="data.seattle.gov")
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": 1}]
        mock_response.raise_for_status = MagicMock()

        with patch.object(client.session, "get", return_value=mock_response) as mock_get:
            records = client.get_records(
                dataset_id="test",
                limit=100,
                offset=50,
                select="id,name",
                where="status='active'",
                order="id DESC",
            )

            call_kwargs = mock_get.call_args
            params = call_kwargs.kwargs["params"]
            assert params["$limit"] == 100
            assert params["$offset"] == 50
            assert params["$select"] == "id,name"
            assert params["$where"] == "status='active'"
            assert params["$order"] == "id DESC"
            assert records == [{"id": 1}]

    @patch.object(SocrataClient, "_build_url", return_value="https://data.seattle.gov/resource/test.json")
    def test_omits_optional_params_when_none(self, mock_url):
        client = SocrataClient(domain="data.seattle.gov")
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()

        with patch.object(client.session, "get", return_value=mock_response) as mock_get:
            client.get_records(dataset_id="test", limit=10, offset=0)

            params = mock_get.call_args.kwargs["params"]
            assert "$select" not in params
            assert "$where" not in params
            assert "$order" not in params


class TestGetAllRecords:
    def test_stops_on_empty_page(self):
        client = SocrataClient(domain="data.seattle.gov")

        with patch.object(client, "get_records", side_effect=[
            [{"id": 1}, {"id": 2}],
            [],
        ]):
            records = client.get_all_records("test", max_records=100, page_size=10)
            assert len(records) == 2

    def test_stops_at_max_records(self):
        client = SocrataClient(domain="data.seattle.gov")
        page = [{"id": i} for i in range(10)]

        with patch.object(client, "get_records", return_value=page):
            records = client.get_all_records("test", max_records=10, page_size=10)
            assert len(records) == 10

    def test_stops_on_partial_page(self):
        client = SocrataClient(domain="data.seattle.gov")

        with patch.object(client, "get_records", side_effect=[
            [{"id": i} for i in range(10)],
            [{"id": 10}, {"id": 11}],
        ]):
            records = client.get_all_records("test", max_records=100, page_size=10)
            assert len(records) == 12
