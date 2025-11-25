from flask import Flask, request, send_file
import zipfile
import os
import subprocess
import uuid

app = Flask(__name__)

@app.route("/convert", methods=["POST"])
def convert_dicom():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files["file"]
    upload_id = str(uuid.uuid4())
    workdir = f"/tmp/{upload_id}"
    os.makedirs(workdir, exist_ok=True)

    zip_path = f"{workdir}/dicom.zip"
    file.save(zip_path)

    # Unzip
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(f"{workdir}/dicom")

    # Run dcm2niix
    outdir = f"{workdir}/nifti"
    os.makedirs(outdir, exist_ok=True)

    subprocess.run(["dcm2niix", "-z", "y", "-o", outdir, f"{workdir}/dicom"], check=True)

    # Find output .nii.gz
    nifti_files = [f for f in os.listdir(outdir) if f.endswith(".nii.gz")]
    if not nifti_files:
        return {"error": "Conversion failed"}, 500

    output_file = f"{outdir}/{nifti_files[0]}"
    return send_file(output_file, as_attachment=True)
    

@app.route("/", methods=["GET"])
def home():
    return {"status": "DICOM → NIfTI API working"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
