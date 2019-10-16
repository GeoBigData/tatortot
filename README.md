# Tatortot
Prototype tool for annotating images.

This package includes one CLI tool:

**tator:**
```
Usage: dipstick [OPTIONS] IMAGE OUT

Options:
  -b, --bbox TEXT  Bbox for subsetting the scene, provided as a comma-
                   delimited string in EPGS:4326 coordinates. e.g.:
                   xmin,ymin,xmax,ymax.Default: None.
  -m, --mode TEXT  Mode for detecting water from the scene.Valid options are:
                   'boot' (more robust to all scenes) and 'global' (better for
                   bimodal scenes)Default: 'boot'
  --help           Show this message and exit.
```
This tool will detect water from a Sentinel-1 scene. This can either be a tif (assumed to be orthorectified and calibrated) or a in image ID.
In the latter case, the image will be accessed via RDA, and calibrated on the fly; however, it will not be orthorectified and therefore may be spatially inaccurate by up to 100s of meters.
This latter mode is best for rapid testing/development purposes.

The default water detection mode is a bootstrapped thresholding approach that is generally robust to non-bimodal images (`--mode boot`)
However, the tool can also be run with a global thresholding approch (`--mode global`), which may produce nicer results for bimodal images.


------------
## TODOS:
-[] r/w from rasterio instead of skimage
-[] refactor to make code simpler, add docs
-[] add box selector feature?
-[] r/w from S3 directories as well as local dirs

------------
## Installation

### Development
#### Requirements:
- General requirements listed above
- Anaconda or Miniconda

#### To set up your local development environment:
This will install the s1_preprocessor package from the local repo in editable mode.
Any changes to Python files within the local repo should immediately take effect in this environment.

1. Clone the repo
`git clone https://github.com/GeoBigData/tatortot.git`

2. Move into the local repo
`cd tatortot`

3. Create conda virtual environment
`conda env create -f environment.yml`

4. Activate the environment
`conda activate tatortot`

5. Install Python package
`pip install -r requirements_dev.txt`

### Common Issues:
- TBD
