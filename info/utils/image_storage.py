
from qiniu import Auth, put_data

# TODO 需要改成自己的
# 需要填写你的 Access Key 和 Secret Key
access_key = 'WvdRdUfofWlGU7r_3kbv5bSj75BpQn4b3RRfFnmj'
secret_key = 'Jk_ZohdpLQI3zmJn5VCvNGZVAwV7n137thzV2Br9'
# 要上传的空间
bucket_name = 'ihome'


def storage(data):

    try:
        # 构建鉴权对象
        q = Auth(access_key, secret_key)

        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name)

        # 上传文件
        ret, info = put_data(token, None, data)
        print(ret,info)

    except Exception as e:

        raise e

    if  info.status_code != 200:
        raise Exception("上传文件到七牛失败")

    # 返回七牛中保存的图片名，这个图片名也是访问七牛获取图片的路径
    return ret["key"]


if __name__ == '__main__':
    file = input("输入上传的文件")
    with open(file, "rb") as f:
        storage(f.read())