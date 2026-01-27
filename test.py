text = "瑨灴㩳⼯楧桴扵挮浯琯湡桡物㉯㄰⼰畡潴牟癥牥敳祟畯畴敢"

# 1. 一旦、UTF-8でバイト列にする
# 2. それをあえて「UTF-16」としてデコードする
# ※バイト数が奇数だとエラーになるため、帳尻を合わせる処理を入れています
raw_bytes = text.encode('utf-16')
if len(raw_bytes) % 2 != 0:
    raw_bytes += b'\x00' # 長さを偶数に調整

mojibake = raw_bytes.decode('utf-8')

print(f"【元の文字列】: {text}")
print(f"【文字化け後】: {mojibake}")