# Reference-Image based Building Recognition (SuperPoint + LightGlue)

Recognizes one specific building in a camera feed from just 1 to 3 reference photos, with no per-building training. Learned feature matching separates the target from other buildings far better than classical methods.

**Author:** Muhammad Haris

## Highlights

- **No training per building:** give the system 1 to 3 photos of a new building and it can look for it.
- **ROC-AUC 0.90 / 0.95 / 0.98** with 1 / 2 / 3 reference photos, against 0.51 to 0.56 for SIFT and 0.66 to 0.69 for ORB on the same photos.
- **With 3 references, 91% of target photos are found with zero false alarms** (68% with 1 reference, 83% with 2).
- **Hard negatives:** against 48 similar-looking buildings (other NUST, Islamabad and glass-facade buildings), ROC-AUC reaches 0.99 with 2 references and 1.00 with 3.
- **Validated on real MaixCAM footage:** all 7 target frames scored 195 to 632 matched points, while all 60 other frames scored 48 or fewer.

## How it works

```
reference photos + camera frame
   -> SuperPoint: detect keypoints and descriptors
   -> LightGlue: match keypoints between the two images
   -> RANSAC (MAGSAC) homography: keep only geometrically consistent matches (inliers)
   -> score = number of inliers; above the cutoff means "this is the target building"
```

The cutoff is chosen from the data. Target photos scored at least 72 inliers, while the best wrong-building score was 39 on the general negatives and 45 to 54 on the hard negatives. A cutoff of about 60 to 80 separates them, and the lock-on pipeline (Project 4) uses 80.

## Results

| Test | Result |
|---|---|
| 32 NSTP photos vs 60 negative photos, SuperPoint + LightGlue, 1 / 2 / 3 references | ROC-AUC 0.90 / 0.95 / 0.98 |
| Same photos, SIFT (1 / 2 / 3 references) | ROC-AUC 0.56 / 0.51 / 0.55 |
| Same photos, ORB (1 / 2 / 3 references) | ROC-AUC 0.66 / 0.67 / 0.69 |
| Target photos found with zero false alarms, 1 / 2 / 3 references | 68% / 83% / 91% |
| 32 NSTP photos vs 48 hard negatives and 20 easy negatives | ROC-AUC 0.99 (2 references), 1.00 (3 references) |
| Real MaixCAM footage, 3 phone reference photos, 7 target frames vs 60 other frames | 195 to 632 inliers vs 48 or fewer; ROC-AUC 1.0 |

Operating range (synthetic test: target photos pasted into other scenes, 2,048 keypoints, 3 references). Share of target images that score above every hard negative:

| Building width as a share of the frame | 40% | 25% |
|---|---|---|
| Share found | 80% | 60% |

A sanity check matched a rotated copy of one image with SIFT (856 of 911 matches were inliers), which confirmed the classical pipeline was implemented correctly.

## Method details

- **Reference crops:** the building is cropped from each labeled reference photo, so only the target is matched.
- **Features:** SuperPoint with 1,024 keypoints (2,048 at higher resolution); images resized to a 600 to 1,000 px longest side.
- **Data:** 32 deduplicated NSTP photos (difference-hash deduplication), general negatives and hard negatives downloaded from Wikimedia Commons, and real footage captured with the MaixCAM.
- **Earlier approaches:** a YOLO classifier and a one-class YOLO26n detector were tried first. The detector found the held-out NSTP photos and produced no detections on the held-out negative images, but it only works for the one building it was trained on, which is why the reference-photo matcher was developed.

## Tech stack

| Area | Tools |
|---|---|
| Matching | SuperPoint, LightGlue (pretrained), OpenCV (MAGSAC homography) |
| Baselines | SIFT, ORB |
| Evaluation | ROC-AUC (scikit-learn) |
| Environment | Python, PyTorch, Google Colab (GPU), MaixCAM as the video source |

## Setup

```bash
pip install git+https://github.com/cvg/LightGlue.git
```

## Usage

Open `Building_Detector.ipynb` in Colab and run the matcher cells in order. Upload three folders when prompted: `ref` (reference photos), `pos` (frames of the target building) and `neg` (frames of other places). The notebook removes near-duplicate frames, matches every frame against the references, and prints the inlier scores and ROC-AUC. Use `capture_frames.py` on the MaixCAM to record the test frames.

## Repository structure

| File | What it is |
|---|---|
| `Building_Detector.ipynb` | Colab notebook: SIFT and ORB baselines, SuperPoint + LightGlue matcher, hard-negative and distance tests, real footage test, lock-on script |
| `capture_frames.py` | MaixPy script: saves one 1280 x 720 frame per second from the MaixCAM into a `pos` or `neg` folder |

Datasets, reference photos and videos are not included.

## Scope

The matching runs on a laptop or a GPU. The MaixCAM provides the camera footage.

## How to run

1. Open `Building_Detector.ipynb` in Colab and set the runtime to a T4 GPU.
2. Run the install cell (LightGlue) and then the matcher cells in order.
3. Prepare three sets of photos: `ref` (2 to 3 whole-building photos of the target), `pos` (frames of the target building) and `neg` (frames of other places). To record frames on the MaixCAM, run `capture_frames.py` in MaixVision with `BATCH = "pos"` at the target and `BATCH = "neg"` elsewhere. Frames are saved in `/root/captures/<BATCH>` on the device. Copy them to your computer and upload them when the notebook asks.
4. Run the test cells. They remove near-duplicate frames, match every frame against the references, and print the inlier scores and the ROC-AUC.

