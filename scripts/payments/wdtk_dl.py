import sys, time, urllib.request, urllib.parse, json, hashlib
from pathlib import Path
SLUGS = ["palantir_contracts_foi_request_u_19","agreement_awarded_to_palantir_te","palantir_contract","palantir_contract_correspondence","redacted_palantir_contract","palantir_nectar_systems","palantir_technologies_use_by_cab","contracts_with_palantir","palantir_technologies_active_con","uon_and_palantir","use_of_palantir_technologies_sof_31","palantir_technologies_products_u_4","palantir_48","palantir_and_nhs_foi_request_73","palantir_and_nhs_foi_request_21","nhs_england_and_palantir","information_regarding_palantir","palantirfederated_data_platform","foi_request_to_the_trust_regardi_97","use_of_palantir_technologies_sof_2","palantir_pilot_project_agreement","access_or_use_of_palantir_techno","palantir_technologies_products_u_3","data_processing_by_palantir_for","freedom_of_information_request_a_1774"]
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
man = []
for line in open(sys.argv[1]):
    i, resp, att, name = line.rstrip("\n").split("|")
    slug = SLUGS[int(i)]
    url = f"https://www.whatdotheyknow.com/request/{slug}/response/{resp}/attach/{att}/{urllib.parse.quote(name)}"
    d = out / slug; d.mkdir(exist_ok=True)
    dest = d / name
    if not dest.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "palantir-uk-open-data/1.0 (public-interest research)"})
        try:
            data = urllib.request.urlopen(req, timeout=120).read()
            dest.write_bytes(data)
            st = "ok"
        except Exception as e:
            st = repr(e)[:100]
        time.sleep(40)
    else:
        st = "exists"
    man.append({"slug": slug, "request_url": f"https://www.whatdotheyknow.com/request/{slug}", "attachment_url": url, "file": str(dest), "status": st})
    print(st, slug, name, file=sys.stderr)
json.dump(man, open(out / "manifest.json", "w"), indent=1)
