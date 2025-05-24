import bcrypt

password = "玉衡在手".encode()
hashed = bcrypt.hashpw(password, bcrypt.gensalt())

print("原始密码：", password)
print("哈希后：", hashed)

# 验证
is_valid = bcrypt.checkpw(password, hashed)
print("验证结果：", is_valid)
