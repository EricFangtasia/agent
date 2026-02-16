import os
import argparse
from OpenSSL import crypto
import time

def generate_self_signed_cert(cert_file="cert.pem", key_file="key.pem", 
                            days=365, cn="localhost"):
    """
    生成自签名SSL证书
    """
    # 创建一个密钥
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    # 创建自签名证书
    cert = crypto.X509()
    cert.get_subject().C = "CN"  # 国家
    cert.get_subject().ST = "State"  # 省份
    cert.get_subject().L = "City"  # 城市
    cert.get_subject().O = "Organization"  # 组织
    cert.get_subject().OU = "OrgUnit"  # 组织单位
    cert.get_subject().CN = cn  # 通用名称
    cert.set_serial_number(int(time.time() * 10000000))  # 序列号
    cert.gmtime_adj_notBefore(0)  # 有效期开始时间
    cert.gmtime_adj_notAfter(days * 24 * 60 * 60)  # 有效期结束时间
    cert.set_issuer(cert.get_subject())  # 颁发者
    cert.set_pubkey(key)  # 设置公钥
    cert.sign(key, 'sha256')  # 用私钥签名

    # 保存证书和私钥
    with open(cert_file, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    
    with open(key_file, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode("utf-8"))

    print(f"自签名SSL证书已生成:")
    print(f"证书文件: {cert_file}")
    print(f"私钥文件: {key_file}")
    print(f"有效期: {days} 天")
    print(f"通用名称: {cn}")

def main():
    parser = argparse.ArgumentParser(description='生成自签名SSL证书')
    parser.add_argument('--cert', type=str, default='cert.pem', 
                        help='证书文件名 (默认: cert.pem)')
    parser.add_argument('--key', type=str, default='key.pem', 
                        help='私钥文件名 (默认: key.pem)')
    parser.add_argument('--days', type=int, default=365, 
                        help='证书有效期天数 (默认: 365)')
    parser.add_argument('--cn', type=str, default='localhost', 
                        help='通用名称 (默认: localhost)')
    
    args = parser.parse_args()
    
    if os.path.exists(args.cert) or os.path.exists(args.key):
        response = input(f"证书文件 {args.cert} 或私钥文件 {args.key} 已存在，是否覆盖? (y/N): ")
        if response.lower() != 'y':
            print("操作已取消")
            return
    
    generate_self_signed_cert(args.cert, args.key, args.days, args.cn)

if __name__ == "__main__":
    main()