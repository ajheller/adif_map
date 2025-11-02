from adimap.adif import parse_adif


def test_parse_simple_adif():
    content = (
        "<CALL:5>TEST1<QSO_DATE:8>20250101<TIME_ON:4>1234<GRIDSquare:4>FN20<EOR>\n"
        "<CALL:5>TEST2<QSO_DATE:8>20250102<TIME_ON:4>2345<LAT:6>40.00N<LON:7>074.0W<EOR>\n"
    )

    records = parse_adif(content)
    assert len(records) == 2
    assert records[0]["CALL"] == "TEST1"
    assert records[1]["CALL"] == "TEST2"
