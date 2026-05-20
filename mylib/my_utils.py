def below_threshold_len(max_len, texts):
    count = 0
    for text in texts:
        if len(text.split()) <= max_len:
            count += 1
    print(f'길이가 {max_len} 이하인 텍스트의 비율 : {count/len(texts) * 100:.4f}%')

def below_threshold_len_from_list(max_len, texts):
    count = 0
    for text in texts:
        if len(text) <= max_len:
            count += 1
    print(f'길이가 {max_len} 이하인 텍스트의 비율 : {count/len(texts) * 100:.4f}%')


def rare_word_status(threshold, word_count_list):
    # 등장 빈도수가 threshold회 미만인 단어들이 이 데이터에서 얼만큼의 비중을 차지하는지 확인

    total_cnt = total_freq = 0
    rare_cnt = rare_freq = 0

    # 단어, 빈도수를 받아서 빈도수가 threshold보다 작으면 rare_cnt, rare_freq update
    for _, freq in word_count_list:
        total_cnt += 1
        total_freq += freq
        if freq < threshold:
            rare_cnt += 1
            rare_freq += freq

    print(f'전체 단어 : {total_cnt:,}개 {total_freq:,}번')
    print(f'희귀 단어(등장빈도 {threshold}번 미만) : {rare_cnt:,}개 {rare_freq:,}번')
    print(f'희귀 단어 비율 : 단어 수 {rare_cnt/total_cnt * 100:.2f}%, 빈도수 {rare_freq/total_freq * 100:.2f}%')
    use_cnt = total_cnt - rare_cnt
    use_freq = total_freq - rare_freq
    print(f'희귀 단어를 뺀 단어 수 : {use_cnt: ,}개 {use_freq/total_freq * 100:.2f}%')