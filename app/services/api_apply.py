import requests

def apply_via_api(url, ats, resume_path):
    print(f"🌐 Submitting application via API → {ats}")

    # NOTE: Each ATS has a different submission format
    # Here we implement the real submission patterns:

    if ats == "lever":
        # Lever application uses JSON + multipart upload
        endpoint = url.replace("/jobs/", "/applications/")
        with open(resume_path, "rb") as f:
            files = {"resume": f}
            data = {"name": "Bryan Ndum", "email": "bryanndum12@gmail.com"}
            r = requests.post(endpoint, data=data, files=files)
            return {"status": r.status_code, "result": r.text}

    elif ats == "greenhouse":
        # Greenhouse uses direct API endpoint
        application_url = url + "/apply"
        with open(resume_path, "rb") as f:
            files = {"attachment": f}
            data = {"first_name": "Bryan", "last_name": "Ndum", "email": "bryanndum12@gmail.com"}
            r = requests.post(application_url, data=data, files=files)
            return {"status": r.status_code, "result": r.text}

    # Add Workable, BambooHR, Ashby, etc. next

    return {"error": "ATS API integration not finished yet"}
