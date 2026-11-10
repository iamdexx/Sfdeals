from sfdeals.util import norm_addr
from sfdeals.stl import city_parcels, county_parcels, inspections, landtax, ms_date


def test_norm_addr_stl():
    assert norm_addr("5860   MAFFITT AV ") == "5860 MAFFITT AVE"
    assert norm_addr("4321 Lindell Boulevard, St. Louis, MO 63108") == "4321 LINDELL BLVD"
    assert norm_addr("12 Main St Florissant MO 63031") == "12 MAIN ST"


def test_city_row():
    r = city_parcels.row({"ParcelId": "03809010000", "HANDLE": "10380000010", "SITEADDR": "1531 S 8TH ST", "ZIP": 63104,
                          "OWNERNAME": "WEBB LINDSEY", "OWNERNAME2": None, "OWNERADDR": "120 S CENTRAL AVE", "OWNERCITY": "CLAYTON",
                          "OWNERSTATE": "mo", "OWNERZIP": "63105-1234", "OWNEROCC": None, "AsrLandUse1": 1110, "NbrOfUnits": 1, "SQFT": 3000,
                          "TaxBalance": 1234.567, "VacBldgYear": 2019, "LendingAgcy": 0, "AsdTotal": 25000, "ResSalePrice": None,
                          "ResSaleDate": 1700000000000, "FirstYearBuilt": 1905})
    assert r["tag"] == "03809010000" and r["addr"] == "1531 S 8TH ST" and r["mail"] == "120 S CENTRAL AVE"
    assert r["mail_state"] == "MO" and r["mail_zip"] == "63105" and r["tax_bal"] == 1234.57 and r["vac_year"] == 2019
    assert r["sale_date"] == "2023-11-14" and r["county"] == "St. Louis City"


def test_county_row():
    r = county_parcels.row({"LOCATOR": "09K230312", "OWNER_NAME": "SMITH JOHN", "PROP_ADD": "123 ELM DR", "PROP_ZIP": "63031",
                            "OWN_ADD": "PO BOX 1", "OWN_CITY": "CHICAGO", "OWN_STATE": "IL", "OWN_ZIP": "60601", "MUNICIPALITY": "FLORISSANT",
                            "TENURE": "NOT OWNER", "LIVUNIT": 1, "YEARBLT": 1960, "RESQFT": 1100, "TOTAPVAL": 150000, "LUCODE": "Single Family"})
    assert r["occ"] == "N" and r["muni"] == "Florissant" and r["mail_state"] == "IL" and r["county"] == "St. Louis County"


def test_inspection_row():
    r = inspections.row({"InspectionID": 1, "CurrentResult": "Notice to Secure", "CurrentResultDate": "2026-11-01T00:00:00", "ProjectAddress": "4200 Page Blvd",
                         "ProjectASRParcelID": "36740001200", "InspectionType": "ES - Complaint",
                         "Violations": [{"ViolationType": "Open to entry", "ViolationSeverity": "Major"}, {"ViolationType": "Weeds", "ViolationSeverity": "Minor"}]})
    assert r["kind"] == "secure" and r["date"] == "2026-11-01" and r["addr"] == "4200 PAGE BLVD" and r["major"] == 1 and r["minor"] == 1
    assert inspections.row({"InspectionID": 2, "CurrentResult": "", "Violations": []}) is None
    assert inspections.row({"InspectionID": 3, "CurrentResult": "Emergency Condemnation and Demo Notice", "Violations": []})["kind"] == "condemned"


def test_landtax_parse():
    rows = landtax.parse("Parcel 44380000350 4500 NATURAL BRIDGE AVE  $3,210.55\nnot a row\n44380000350 dup")
    assert rows == [{"pid": "44380000350", "addr": "4500 NATURAL BRIDGE AVE", "line": "Parcel 44380000350 4500 NATURAL BRIDGE AVE  $3,210.55"}]
    assert ms_date(None) == "" and ms_date(0) == ""
