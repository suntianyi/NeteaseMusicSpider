import base64
import json
import os
from binascii import hexlify

import requests
from Crypto.Cipher import AES

'''
音乐下载
'''


headers = {'Origin': 'https://music.163.com',
           'Content-Type': 'application/x-www-form-urlencoded',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'}


class Encrypyed:
    """
    传入歌曲的ID，加密生成'params'、'encSecKey
    """

    def __init__(self):
        self.pub_key = '010001'
        self.modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        self.nonce = b'0CoJUm6Qyw8W8jud'

    def create_secret_key(self, size):
        return hexlify(os.urandom(size))[:16].decode('utf-8')

    def aes_encrypt(self, text, key):
        iv = b'0102030405060708'
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        text = text.encode("utf-8")
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        result = encryptor.encrypt(text)
        result_str = base64.b64encode(result).decode('utf-8')
        return result_str

    def rsa_encrpt(self, text, pubKey, modulus):
        text = text[::-1]
        rs = pow(int(hexlify(text), 16), int(pubKey, 16), int(modulus, 16))
        return format(rs, 'x').zfill(256)

    def work(self, text):
        text = json.dumps(text)
        i = self.create_secret_key(16).encode("utf-8")
        encText = self.aes_encrypt(text, self.nonce)
        encText = self.aes_encrypt(encText, i)
        encSecKey = self.rsa_encrpt(i, self.pub_key, self.modulus)
        data = {'params': encText, 'encSecKey': encSecKey}
        return data


def get_download_url(url):
    song_id = url.split('=')[-1]
    text = {'ids': [song_id], 'br': '128000', 'csrf_token': ''}
    response = requests.post('https://music.163.com/weapi/song/enhance/player/url?csrf_token=', headers=headers, data=Encrypyed().work(text)).text
    j = json.loads(response)
    return j['data'][0]['url']


def download(download_url, path, song_name):
    r = requests.get(download_url, stream=True)
    with open(path + '/' + song_name + '.mp3', "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


if __name__ == '__main__':
    path = 'E:/CloudMusic'
    song_name = '脱单告急'
    url = 'https://music.163.com/#/song?id=1311101979'
    download_url = get_download_url(url)
    print(download_url)
    download(download_url, path, song_name)
