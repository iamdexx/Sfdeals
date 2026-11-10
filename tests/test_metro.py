from sfdeals.metro import parcels, signals, metros


SPEC = metros.METROS["phx"]["counties"][0]["parcels"]


def test_metro_parcel_row():
    a = {"APN": "10221040", "PHYSICAL_STREET_NUM": "2911", "PHYSICAL_STREET_DIR": "N", "PHYSICAL_STREET_NAME": "71ST", "PHYSICAL_STREET_TYPE": "DR",
         "PHYSICAL_STREET_POSTDIR": None, "PHYSICAL_ZIP": "85033", "PHYSICAL_CITY": "PHOENIX", "OWNER_NAME": "ZUBIATE GEORGINA",
         "MAIL_ADDR1": "PO BOX 12", "MAIL_CITY": "MESA", "MAIL_STATE": "az", "MAIL_ZIP": "85201-1234", "PUC": "0131", "CONST_YEAR": "1979",
         "LIVING_SPACE": "   1,572", "FCV_CUR": "     281,300", "SALE_DATE": "07/01/2018", "SALE_PRICE": "160850"}
    r = parcels.row(a, SPEC, "Maricopa County", "AZ")
    assert r["addr"] == "2911 N 71ST DR" and r["mail"] == "PO BOX 12" and r["mail_state"] == "AZ" and r["mail_zip"] == "85201"
    assert r["value"] == 281300 and r["res_sqft"] == 1572 and r["year"] == 1979 and r["sale_price"] == 160850
    assert parcels.fields(SPEC).startswith("APN,PHYSICAL_STREET_NUM")


def test_metro_signal_row():
    s = metros.METROS["phx"]["counties"][0]["signals"][1]
    r = signals.row({"APN": "10104006D", "PropertyFullStreetAddress": "182 S 95th Ave", "TreasurerWebLink": "https://t/x"}, s)
    assert r == {"sig": "taxlien", "weight": 35, "label": "delinquent tax, lien list", "tag": "10104006D", "addr": "182 S 95TH AVE", "link": "https://t/x"}
