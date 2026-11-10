# Phoenix (Maricopa County) sources

Working, free, unattended:
- Assessor parcels: `services.arcgis.com/ykpntM6e3tHvzKRJ/.../Parcels_view/FeatureServer/0` (T_PARCELS, 1.76M; owner, mailing address, PUC land use, FCV, sale). Residential is `PUC LIKE '01%'` (1.23M). Absentee pulled server-side with `MAIL_ZIP <> PHYSICAL_ZIP OR MAIL_STATE <> 'AZ'` (284k); same-zip absentee owners are missed on purpose to keep the pull under 10 minutes.
- Treasurer lien layers: `.../ParcelLienDelinquent/FeatureServer` layer 1 "Unsold Lien Parcels" (state held, 1.5k) and layer 2 "Delinquent Tax Parcels" (37.7k), with treasurer and recorder links per parcel.

Next, not yet wired: City of Phoenix code enforcement cases (open data portal), Maricopa recorder notices of trustee sale (recorder.maricopa.gov search, check terms), Maricopa Justice Court evictions.
