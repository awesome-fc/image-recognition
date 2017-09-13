# image-recognition

场景：图像自动分类，用户通过oss上传图片，触发函数计算服务进行图像识别，并且按照识别的结果进行分类存储
方案分析： 
     step1：通过OSS的Put或者Post事件的触发函数计算服务 
     step2：函数服务里通过调用阿里云的图像识别服务，实时分析出图片内容 
     step3：解析识别的结果，归类存储到OSS不同的bucket中 
前置准备： 
     step1: 开通日志服务，并授权函数服务 
     step2: 开通oss，并创建3个bucket， one bucket for watching，two buckets for 'plant, animal' image 
     step3: 开通图像识别服务
    
