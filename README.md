# Tatortot
Prototype tool for annotating images.

This package includes one CLI tool:

**tator:**
```
Usage: tator [OPTIONS] SRC DEST

Options:
  -C, --overlay_color TEXT     Color to use for overlay. Valid options are: 'b
                               lue','orange','green','red','purple','brown','p
                               ink','gray','olive','cyan'.Defualt: 'cyan'.
  -A, --overlay_alpha FLOAT    Transparency to use for overlay provided as
                               alpha value (0-1).Default: 0.3.
  -w, --img_width INTEGER      Width of src images in pixels. Default is 256
  -h, --img_height INTEGER     Height of src images in pixels. Default is 256
  -W, --viewer_width INTEGER   Width of viewer in pixels. Default is 325
  -H, --viewer_height INTEGER  Height of viewer in pixels. Default is 800
  -f, --filetype TEXT          File format for src images (as file extension).
                               Default is '.jpeg'
  --help                       Show this message and exit.



Note: SRC and DEST should both be local directories. SRC should contain images to annotate, DEST will store results.
```

This utility provides a simple interface for performing image annotation, and specifically defining binary semantic segmentation.


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
