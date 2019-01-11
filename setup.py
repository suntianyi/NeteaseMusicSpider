from setuptools import setup, find_packages

setup(
    name="netease_music_spider",
    version="1.0",
    author="zhsun5",
    author_email="1298935716@qq.com",
    description="网易云音乐爬虫",
    packages=find_packages(),
    install_requires=["requests>=2.18.4",
                      "redis>=2.10.6",
                      "pymysql>=0.8.0",
                      "DBUtils", 'schedule'
                      ]
)
