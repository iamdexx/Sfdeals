from sfdeals.util import norm_addr
from sfdeals import sheriff, delinquent


def test_norm_addr():
    assert norm_addr("1400 E 24th St SFSD 57105") == "1400 E 24TH ST"
    assert norm_addr("4900 W. Cayman Street, Sioux Falls, SD 57107") == "4900 W CAYMAN ST"
    assert norm_addr("2613 N Sweet Grass Avenue Apt 4") == "2613 N SWEET GRASS AVE"


def test_sheriff_parse():
    txt = "### Wednesday, December 2nd, 2026\n49CIV25-004733 IDAHO HOUSING AND FINANCE ASSOCIATION VS MACY TRAUTNER (HALLIDAY). 1400 E 24TH ST SFSD 57105. JUDGMENT AMT $240,254.36\n"
    r = sheriff.parse(txt, "upcoming")
    assert len(r) == 1 and r[0]["addr"] == "1400 E 24TH ST" and r[0]["judgment"] == 240254.36 and r[0]["sale_date"] == "2026-12-02"
    txt2 = "### Wednesday, August 19th, 2026\n49CIV25-001111 BANK VS JOHN DOE (X). 100 N MAIN AVE SFSD 57104. JUDGMENT AMT $100,000.00 BID BY TUCKER PROPERTY HOLDINGS $120,500.00\n"
    r2 = sheriff.parse(txt2, "result")
    assert r2[0]["bidder"] == "TUCKER PROPERTY HOLDINGS" and r2[0]["bid"] == 120500.0


def test_delinquent_row():
    m = delinquent.ROW.match("406 22nd LLC 035270 $30980.58 S1/2 Lots 39 & 40 Block 7 Highland Addn")
    assert m and m.group(2) == "035270" and m.group(3) == "30980.58"
