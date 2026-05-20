def below_threshold_len(max_len, texts):
    count = 0
    for text in texts:
        if len(text.split()) <= max_len:
            count += 1
    print(f'길이가 {max_len} 이하인 텍스트의 비율 : {count/len(texts) * 100:.4f}%')

