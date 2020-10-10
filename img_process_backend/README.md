# Image Classification

Firstly, you can try it out with Python to train a model for image classification, such model will be packaged as a BentoML package for easier deplyment afterwords.
There will be some imeges from CIFAR-10 poping out as well for you to understand how it works for image classification.
```python
python3 bentoml_img_classify.py
```

As for me, the newly generated BentoML packages will be stored at:
```
/Users/yidawang/bentoml/repository/PytorchImageSegment/
```

Such BentoML package for image classfication is already placed in `bentoml_package_cls` folder, you can execute it with 
```bash
bentoml run PytorchImageClassifier:latest predict  --input-file=dog.jpg
```

Then following infos will be printed:
```
INFO - {'service_name': 'PytorchImageClassifier', 'service_version': '20201008191758_DAF5E5', 'api': 'predict', 'task': {'data': {'uri': 'file:///Users/yidawang/Documents/gitfarm/Flask-ML/img_process_backend/dog.jpg', 'name': 'dog.jpg'}, 'task_id': 'e2dedc9f-b6eb-4116-950c-ad71e66b0f7f', 'cli_args': ('--input-file=dog.jpg',)}, 'result': {'data': '"cat"', 'http_status': 200, 'http_headers': (('Content-Type', 'application/json'),)}, 'request_id': 'e2dedc9f-b6eb-4116-950c-ad71e66b0f7f'}
```

Now I successfullly package classification with BentoML, segmentation only works for running with Python rather than BentoML with packaged model.

# Image Segmentation
For sake of a good demo, I believe that we need the segmentation as richer API, now it works with Python

```python
python3 bentoml_img_segment.py
```
Then a new folder containing all bentoML services like:
```
/Users/yidawang/bentoml/repository/PytorchImageSegment/20201010015248_3360B3
├── Dockerfile
├── MANIFEST.in
├── PytorchImageSegment
│   ├── __init__.py
│   ├── __pycache__
│   │   └── pytorch_image_segment.cpython-37.pyc
│   ├── artifacts
│   │   ├── __init__.py
│   │   └── net.pt
│   ├── bentoml.yml
│   └── pytorch_image_segment.py
├── README.md
├── bentoml-init.sh
├── bentoml.yml
├── docker-entrypoint.sh
├── environment.yml
├── python_version
├── requirements.txt
└── setup.py
```

Such BentoML package for image classfication is already placed in `bentoml_package_seg` folder, you can execute it with 
```bash
bentoml run PytorchImageSegment:latest predict  --input-file=images/trees.jpg
bentoml run PytorchImageSegment:latest predict  --input-file=images/street.jpg
bentoml run PytorchImageSegment:latest predict  --input-file=images/pig.jpg
bentoml run PytorchImageSegment:latest predict  --input-file=images/dog.jpg
```
The predicted result would look like followings:
| Input image | Estimated segment |
:-------------------------:|:-------------------------:
 <img src="images/dog.jpg" alt="road condition" frameborder="0" style="border:0" > | <img src="images/dog_seg.png" alt="road condition" frameborder="0" style="border:0" >
 <img src="images/people.jpg" alt="road condition" frameborder="0" style="border:0" > | <img src="images/people_seg.png" alt="road condition" frameborder="0" style="border:0" >
 <img src="images/street.jpg" alt="road condition" frameborder="0" style="border:0" > | <img src="images/street_seg.png" alt="road condition" frameborder="0" style="border:0" >
 <img src="images/pig.jpg" alt="road condition" frameborder="0" style="border:0" > | <img src="images/pig_seg.png" alt="road condition" frameborder="0" style="border:0" >
