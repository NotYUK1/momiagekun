import subprocess
from janome.tokenizer import Tokenizer

def creat_WAV(inputText):
        #message.contentをテキストファイルに書き込み
    input_file = 'input.txt'
    t = Tokenizer()
    res = t.tokenize(inputText)
    data = []
    for all in res:
        tex = all.surface
        if all.part_of_speech.split(",")[0] == u"名詞":
            tex = "おしり"
        data.append(tex)
    intext = ''.join(data)

    with open(input_file,'w',encoding='shift_jis') as file:
        file.write(intext)

    command = 'C:/open_jtalk/bin/open_jtalk -x {x} -m {m} -r {r} -ow {ow} {input_file}'

    #辞書のPath
    x = 'C:/open_jtalk/bin/dic'

    #ボイスファイルのPath
    m = 'C:/open_jtalk/bin/mei/mei_normal.htsvoice'

    #発声のスピード
    r = '1.0'

    #出力ファイル名　and　Path
    ow = 'output.wav'

    args= {'x':x, 'm':m, 'r':r, 'ow':ow, 'input_file':input_file}

    cmd= command.format(**args)
    print(cmd)

    subprocess.run(cmd)
    return True

if __name__ == '__main__':
    creat_WAV('テスト')