Image recognition template for aliyun FunctionCompute
=======
this function service can classified pictures depend on the result of image recognition.

> This project depend on [image recognition](https://help.aliyun.com/knowledge_detail/53540.html) service，you need open this service firstly.

### Steps:
* create one log project and log store :https://help.aliyun.com/document_detail/54604.html
* create two buckets:https://promotion.aliyun.com/ntms/act/ossdoclist.html, one for watching, one for storing the different kind of pictures.
* create one function: watching the source bucket, when one picture was post, this function will be triggered. setup function compute service :https://help.aliyun.com/document_detail/51733.html


### scenarios:
* put/post one picture into the source bucket
* trigger function to classify this picture
* store into bucket with different folder.

### How to set up function:
* create local folder: code , and download image-recognition-demo.py into into this folder.
* use fcli client.
```
    >> fcli shell
    >> mks demo
    >> cd demo
    >> mkf image_recognition -h image_recognition.handler -d code -t python2.7
```
* create one trigger : https://help.aliyun.com/document_detail/53097.html

