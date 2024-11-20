import pandas

def filter_stn(input_file, output_file):
    df = pandas.read_csv(input_file)
    df = df[~df['final_sentence'].str.contains(":", na=False)]
    df = df[~df['final_sentence'].str.contains("exactly", na=False)]
    df = df[~df['final_sentence'].str.contains("elementary school student", na=False)]
    df = df[~df['final_sentence'].str.contains("elementary school students", na=False)]

    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"필터링 완료. 파일이 저장되었습니다: {output_file}")