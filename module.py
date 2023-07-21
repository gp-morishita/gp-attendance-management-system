# coding: utf-8




#モジュールの読み込み
import os
import re
import cv2
import numpy
import random
import datetime
import emoji
from PIL import Image
from janome.tokenizer import Tokenizer




IMAGE_DIRECTORY = "static/cache_images/"




#テキストを解析する
def analyze_text(txts):
    txt_mean   = []
    txt_tkns   = []
    txt_sntmnt = "テキスト感情:実装予定"
    txt_djst   = "テキスト要約:実装予定"
    txts_idx   = 0


    spltd_txts = split_text_into_lines(txts)

    while txts_idx < len(spltd_txts):
          orign_txt          = spltd_txts[txts_idx]
          rmvd_and_short_txt = remove_and_shortening_symbols(orign_txt)

          extrctd_intnt = extract_intent_from_gag_and_vocal_cord_copy(rmvd_and_short_txt)
          if extrctd_intnt != "不明・その他":
             txt_mean.append([orign_txt, \
                              "無し", rmvd_and_short_txt, \
                              "無し", "無し", \
                              "無し", "無し", \
                              extrctd_intnt, rmvd_and_short_txt])

             txt_tkns.append(token_analyze_to_text_out(orign_txt))
             txts_idx += 1
             continue

          extrctd_intnt = extract_intent_from_short_and_boilerplate_for_child(rmvd_and_short_txt)
          if extrctd_intnt != "不明・その他":
             txt_mean.append([orign_txt, \
                              "無し", rmvd_and_short_txt, \
                              "無し", "無し", \
                              "無し", "無し", \
                              extrctd_intnt, rmvd_and_short_txt])

             txt_tkns.append(token_analyze_to_text_out(orign_txt))
             txts_idx += 1
             continue

          extrctd_intnt = extract_intent_from_short_and_boilerplate_for_adlut(rmvd_and_short_txt)
          if extrctd_intnt != "不明・その他":
             txt_mean.append([orign_txt, \
                              "無し", rmvd_and_short_txt, \
                              "無し", "無し", \
                              "無し", "無し", \
                              extrctd_intnt, rmvd_and_short_txt])

             txt_tkns.append(token_analyze_to_text_out(orign_txt))
             txts_idx += 1
             continue

          extrctd_cntnt,     extrctd_cntnt_txt     = extract_content(rmvd_and_short_txt)
          extrctd_1st_cnnct, extrctd_1st_cnnct_txt = extract_1st_connect(rmvd_and_short_txt)
          extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt = extract_2nd_connect(rmvd_and_short_txt)
          extrctd_intnt,     extrctd_intnt_txt     = extract_intent_from_general_text(extrctd_cntnt_txt)
          txt_mean.append([orign_txt, \
                           extrctd_cntnt, extrctd_cntnt_txt, \
                           extrctd_1st_cnnct, extrctd_1st_cnnct_txt, \
                           extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt, \
                           extrctd_intnt, extrctd_intnt_txt])

          txt_tkns.append(token_analyze_to_text_out(orign_txt))
          txts_idx += 1


    return txts, txt_mean, txt_tkns, txt_sntmnt, txt_djst


#テキストを一行単位に分割する
def split_text_into_lines(txts):
    anlyzd_tkns = token_analyze(txts)
    spltd_txts1 = []
    spltd_txts2 = []
    ln_str      = ""
    tkns_cnt    = 0


    for anlyzd_tkn in anlyzd_tkns:
        tkns_cnt += 1

    else:

        if tkns_cnt == 1:
           if (anlyzd_tkn != "\r" and anlyzd_tkn != "\n"):
               spltd_txts1.append(anlyzd_tkn)

           return spltd_txts1

    for anlyzd_tkn in anlyzd_tkns:
        if (anlyzd_tkn != "\r" and anlyzd_tkn != "\n"):
            spltd_txts1.append(anlyzd_tkn)

    for   spltd_tkn in spltd_txts1:
          if  spltd_tkn != "。":
              ln_str += spltd_tkn

          else:

              ln_str += "。"
              spltd_txts2.append(ln_str)
              ln_str = ""

    else:

          if ln_str != "":
             spltd_txts2.append(ln_str)


    return spltd_txts2


#テキストがゼロ行(＝全くない)かを判定する
def check_text_not_exist(txts):
    spltd_txts = split_text_into_lines(txts)

    if len(spltd_txts) == 0:

       return True

    else:

       return False


#テキストが単一の行かを判定する
def check_text_single_line(txts):
    spltd_txts = split_text_into_lines(txts)

    if len(spltd_txts) == 1:

       return True

    else:

       return False


#テキストが複数の行かを判定する
def check_text_multi_line(txt):
    spltd_txts = split_text_into_lines(txts)

    if len(spltd_txts) > 1:

       return True

    else:

       return False


#テキストが指定の文字列で開始するかを判定する
def check_text_start_string(txt, pttrn_str):
    is_strt = txt.startswith(pttrn_str)

    return is_strt


#テキストが指定の文字列で終結するかを判定する(改行コードを終端とする)
def check_text_terminate_string(txt, pttrn_str):
    is_trmnt = txt.endswith(pttrn_str)

    return is_trmnt


#テキストの形態素解析をする(見出し＆表層形のみをリストにして出力する)
def token_analyze(txts):
    tknzr           = Tokenizer()
    txt_tkns        = tknzr.tokenize(txts)
    result_txt_tkns = []

    for anlyzd_tkn in txt_tkns:
        result_txt_tkns.append(anlyzd_tkn.surface)


    return result_txt_tkns


#テキストを形態素解析する(見出し＆表層形と品詞の組をリストにして出力する)
def token_analyze2(txts):
    tknzr       = Tokenizer()
    txt_tkns    = tknzr.tokenize(txts)
    result_tkns = []

    for anlyzd_tkn in txt_tkns:
        result_tkns.append([anlyzd_tkn.surface, anlyzd_tkn.part_of_speech])


    return result_tkns


#テキストを字句解析して結果(＝Janomeによるもの)を出力する
def token_analyze_to_text_out(txt):
    txt_tkns   = []
    anlyzd_txt = ""
    tkns_idx   = 0


    rmvd_symbl_txt     = remove_symbols(txt)
    rmvd_emoji_txt     = remove_emoji(rmvd_symbl_txt)
    rmvd_emotnl_txt    = remove_emotional(rmvd_emoji_txt)
    rmvd_fnl_prtcl_txt = remove_final_particle(rmvd_emotnl_txt)
    rmvd_1st_cnnct_txt = remove_1st_connect(rmvd_fnl_prtcl_txt)
    extrctd_cntnt_txt  = rmvd_1st_cnnct_txt

    tkns = token_analyze2(extrctd_cntnt_txt)

    while tkns_idx < len(tkns):
          txt_tkns.append("<" + tkns[tkns_idx][0] + " " + tkns[tkns_idx][1] + ">")
          tkns_idx += 1

    for anlyzd_tkn in txt_tkns:
        anlyzd_txt += anlyzd_tkn

    return anlyzd_txt


#テキストを字句解析して結果(＝名詞同士、体言＆用言同士を連結＆連体したもの)を出力する
def token_analyze_to_text_out2(txt):
    txt_tkns   = []
    anlyzd_txt = ""
    tkns_idx   = 0


    rmvd_symbl_txt     = remove_symbols(txt)
    rmvd_emoji_txt     = remove_emoji(rmvd_symbl_txt)
    rmvd_emotnl_txt    = remove_emotional(rmvd_emoji_txt)
    rmvd_fnl_prtcl_txt = remove_final_particle(rmvd_emotnl_txt)
    rmvd_1st_cnnct_txt = remove_1st_connect(rmvd_fnl_prtcl_txt)
    rmvd_2nd_cnnct_txt = remove_2nd_connect(rmvd_1st_cnnct_txt)
    extrctd_cntnt_txt  = rmvd_2nd_cnnct_txt

    tkns = token_analyze2(extrctd_cntnt_txt)

    tkns = join_tokens_by_noun(tkns)
    tkns = join_tokens_by_noun_between_jp_no(tkns)
    tkns = join_tokens_by_verb_and_auxiliary_verb(tkns)
    tkns = join_tokens_by_verbs_and_conjunctive_particle(tkns)
    tkns = join_tokens_by_verbs_conjunctive_particle_and_verbs(tkns)
    tkns = join_tokens_by_jp_to_as_case_particle_and_jp_ha_as_participant_particle(tkns)

    while tkns_idx < len(tkns):
          txt_tkns.append("<" + tkns[tkns_idx][0] + " " + tkns[tkns_idx][1] + ">")
          tkns_idx += 1

    for anlyzd_tkn in txt_tkns:
        anlyzd_txt += anlyzd_tkn

    return anlyzd_txt


#テキストの中に含まれる各種の記号列を短縮する
def remove_and_shortening_symbols(txt):
    rmvd_symbl_txt = re.sub("(’)", "", txt)
    rmvd_symbl_txt = re.sub("(”)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(「)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(」)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(、)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(。)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(・)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(･)",  "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(＆)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(＃)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(＠)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(＊)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(／)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(　)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\')", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\")", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\()", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\))", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\[)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\])", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\,)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\.)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\:)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\;)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\-)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\=)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\^)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\~)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\&)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\#)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\@)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("( )",  "", rmvd_symbl_txt)
    rmvd_and_short_txt = re.sub(r"(！)+", "", rmvd_symbl_txt)
    rmvd_and_short_txt = re.sub(r"(？)+", "", rmvd_and_short_txt)
    rmvd_and_short_txt = re.sub(r"(♪)+", "", rmvd_and_short_txt)
    rmvd_and_short_txt = re.sub(r"(～)+", "", rmvd_and_short_txt)
    rmvd_and_short_txt = re.sub(r"(―)+", "", rmvd_and_short_txt)
    rmvd_and_short_txt = re.sub(r"(\!)+", "", rmvd_and_short_txt)
    rmvd_and_short_txt = re.sub(r"(\?)+", "", rmvd_and_short_txt)


    return rmvd_and_short_txt


#テキストの中に含まれる各種の記号や空白を除去する
def remove_symbols(txt):
    rmvd_symbl_txt = re.sub("(’)", "", txt)
    rmvd_symbl_txt = re.sub("(”)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(「)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(」)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(、)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(。)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(・)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(･)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(＆)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(＃)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(＠)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(＊)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(／)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(　)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\')", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\")", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\()", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\))", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\[)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\])", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\,)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\.)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\:)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\;)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\!)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\?)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\-)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\=)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\^)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\~)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\&)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\#)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\@)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("(\/)", "", rmvd_symbl_txt)
    rmvd_symbl_txt = re.sub("( )",  "", rmvd_symbl_txt)


    return rmvd_symbl_txt


#テキストの中に含まれる各種の絵文字を除去する
def remove_emoji(txt):
    rmvd_emoji_txt = emoji.replace_emoji(txt)


    return rmvd_emoji_txt


#テキストの中に含まれる感情表現のためのものを除去する
def remove_emotional(txt):
    #テキストの中に含まれるその他のものを除去する
    if   bool(re.search(r"怒$",      txt)) == True:
         rmvd_emotnl_txt = re.sub(r"怒$",      "", txt)
    elif bool(re.search(r"泣$",      txt)) == True:
         rmvd_emotnl_txt = re.sub(r"泣$",      "", txt)
    elif bool(re.search(r"汗$",      txt)) == True:
         rmvd_emotnl_txt = re.sub(r"汗$",      "", txt)
    elif bool(re.search(r"爆$",      txt)) == True:
         rmvd_emotnl_txt = re.sub(r"爆$",     "", txt)
    elif bool(re.search(r"(爆笑)$",  txt)) == True:
         rmvd_emotnl_txt = re.sub(r"(爆笑)$", "", txt)
    elif bool(re.search(r"(大爆笑)$",txt)) == True:
         rmvd_emotnl_txt = re.sub(r"(大爆笑)$", "", txt)
    elif bool(re.search(r"(大笑)$",  txt)) == True:
         rmvd_emotnl_txt = re.sub(r"(大笑)$", "", txt)
    elif bool(re.search(r"(失笑)$",  txt)) == True:
         rmvd_emotnl_txt = re.sub(r"(失笑)$", "", txt)
    elif bool(re.search(r"(苦笑)$",  txt)) == True:
         rmvd_emotnl_txt = re.sub(r"(苦笑)$", "", txt)
    elif bool(re.search(r"(冷笑)$",  txt)) == True:
         rmvd_emotnl_txt = re.sub(r"(冷笑)$", "", txt)
    elif bool(re.search(r"笑+$",     txt)) == True:
         rmvd_emotnl_txt = re.sub(r"笑+$",     "", txt)
    elif bool(re.search(r"(わら)+$", txt)) == True:
         rmvd_emotnl_txt = re.sub(r"(わら)+$", "", txt)
    elif bool(re.search(r"(ワラ)+$", txt)) == True:
         rmvd_emotnl_txt = re.sub(r"(ワラ)+$", "", txt)
    elif bool(re.search(r"草+$",     txt)) == True:
         rmvd_emotnl_txt = re.sub(r"草+$",     "", txt)
    elif bool(re.search(r"(くさ)+$", txt)) == True:
         rmvd_emotnl_txt = re.sub(r"(くさ)+$", "", txt)
    elif bool(re.search(r"(クサ)+$", txt)) == True:
         rmvd_emotnl_txt = re.sub(r"(クサ)+$", "", txt)
    elif bool(re.search(r"w+$",      txt)) == True:
         rmvd_emotnl_txt = re.sub(r"w+$",      "", txt)
    elif bool(re.search(r"W+$",      txt)) == True:
         rmvd_emotnl_txt = re.sub(r"W+$",      "", txt)
    else:
         rmvd_emotnl_txt = txt


    return rmvd_emotnl_txt


#テキストの中に含まれる終助詞を除去する
def remove_final_particle(txt):
    if   bool(re.search(r"の$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"の$",   "", txt)
    elif bool(re.search(r"よお$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"よお$", "", txt)
    elif bool(re.search(r"よぉ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"よぉ$", "", txt)
    elif bool(re.search(r"よっ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"よっ$", "", txt)
    elif bool(re.search(r"よ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"よ$",   "", txt)
    elif bool(re.search(r"ねえ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"ねえ$", "", txt)
    elif bool(re.search(r"ねぇ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"ねぇ$", "", txt)
    elif bool(re.search(r"ねっ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"ねっ$", "", txt)
    elif bool(re.search(r"ね$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"ね$",   "", txt)
    elif bool(re.search(r"なあ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"なあ$", "", txt)
    elif bool(re.search(r"なぁ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"なぁ$", "", txt)
    elif bool(re.search(r"なっ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"なっ$", "", txt)
    elif bool(re.search(r"な$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"な$",   "", txt)
    elif bool(re.search(r"わあ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"わあ$", "", txt)
    elif bool(re.search(r"わぁ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"わぁ$",   "", txt)
    elif bool(re.search(r"わっ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"わっ$",   "", txt)
    elif bool(re.search(r"わ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"わ$",     "", txt)
    elif bool(re.search(r"ぜえ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"ぜえ$",   "", txt)
    elif bool(re.search(r"ぜぇ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"ぜぇ$",   "", txt)
    elif bool(re.search(r"ぜっ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"ぜっ$",   "", txt)
    elif bool(re.search(r"ぜ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"ぜ$",     "", txt)
    elif bool(re.search(r"ぞよ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"ぞよ$",   "", txt)
    elif bool(re.search(r"ぞ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"ぞ$",     "", txt)
    elif bool(re.search(r"っすよ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"っすよ$",   "", txt)
    elif bool(re.search(r"っすね$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"っすね$",   "", txt)
    elif bool(re.search(r"でっす$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"でっす$",   "", txt)
    elif bool(re.search(r"っす$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"っす$",     "", txt)
    elif bool(re.search(r"わよ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"わよ$",     "", txt)
    elif bool(re.search(r"わよっ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"わよっ$",   "", txt)
    elif bool(re.search(r"わね$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"わね$",     "", txt)
    elif bool(re.search(r"わねっ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"わねっ$",   "", txt)
    elif bool(re.search(r"ってね$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"ってね$",   "", txt)
    elif bool(re.search(r"ってば$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"ってば$",   "", txt)
    elif bool(re.search(r"ってばよ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"ってばよ$", "", txt)
    elif bool(re.search(r"っ$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"っ$",       "", txt)
    elif bool(re.search(r"から$", txt)):
         rmvd_finl_partcl_txt = re.sub(r"から$",     "", txt)
    else:
         rmvd_finl_partcl_txt = txt


    return rmvd_finl_partcl_txt


#テキストの中に含まれる第一のコネクト(＝前文との接続の種類＆類型)を除去する
def remove_1st_connect(txt):
    if   bool(re.search(r"^そうして",       txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^そうして",       "", txt)
    elif bool(re.search(r"^そして", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^そして",         "", txt)
    elif bool(re.search(r"^それで",       txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^それで",         "", txt)
    elif bool(re.search(r"^だから",       txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^だから",         "", txt)
    elif bool(re.search(r"^従って",       txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^従って",         "", txt)
    elif bool(re.search(r"^したがって",   txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^したがって",     "", txt)
    elif bool(re.search(r"^なので",       txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^なので",         "", txt)
    elif bool(re.search(r"^そこで",       txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^そこで",         "", txt)
    elif bool(re.search(r"^すると",       txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^すると",         "", txt)
    elif bool(re.search(r"^しかし",       txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^しかし",         "", txt)
    elif bool(re.search(r"^だが",         txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^だが",           "", txt)
    elif bool(re.search(r"^でも",         txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^でも",           "", txt)
    elif bool(re.search(r"^けれども",     txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^けれども",       "", txt)
    elif bool(re.search(r"^所が",         txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^所が",           "", txt)
    elif bool(re.search(r"^ところが",     txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^ところが",       "", txt)
    elif bool(re.search(r"^尚も",         txt)): 
         rmvd_1st_cnnct_txt = re.sub(r"^尚も",           "", txt)
    elif bool(re.search(r"^なおも",       txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^なおも",         "", txt)
    elif bool(re.search(r"^加えれば", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^加えれば",       "", txt)
    elif bool(re.search(r"^加えると", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^加えると",       "", txt)
    elif bool(re.search(r"^加えて", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^加えて",         "", txt)
    elif bool(re.search(r"^あと",         txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^あと",           "", txt)
    elif bool(re.search(r"^又",           txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^又",             "", txt)
    elif bool(re.search(r"^また",         txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^また",           "", txt)
    elif bool(re.search(r"^そして",       txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^そして",         "", txt)
    elif bool(re.search(r"^尚",           txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^尚",             "", txt)
    elif bool(re.search(r"^なお",         txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^なお",           "", txt)
    elif bool(re.search(r"^且つ",         txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^且つ",           "", txt)
    elif bool(re.search(r"^かつ",         txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^かつ",           "", txt)
    elif bool(re.search(r"^それとも",     txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^それとも",       "", txt)
    elif bool(re.search(r"^又は",         txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^又は",           "", txt)
    elif bool(re.search(r"^または",       txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^または",         "", txt)
    elif bool(re.search(r"^若しくは",     txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^若しくは",       "", txt)
    elif bool(re.search(r"^もしくは",     txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^もしくは",       "", txt)
    elif bool(re.search(r"^詰まりは",     txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^詰まりは",       "", txt)
    elif bool(re.search(r"^つまりは",     txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^つまりは",       "", txt)
    elif bool(re.search(r"^詰まり",       txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^詰まり",         "", txt)
    elif bool(re.search(r"^つまり",       txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^つまり",         "", txt)
    elif bool(re.search(r"^何故ならば",   txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^何故ならば",     "", txt)
    elif bool(re.search(r"^なぜならば",     txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^なぜならば",     "", txt)
    elif bool(re.search(r"^何故なら",     txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^何故なら",       "", txt)
    elif bool(re.search(r"^なぜなら",     txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^なぜなら",       "", txt)
    elif bool(re.search(r"^所で",         txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^所で",           "", txt)
    elif bool(re.search(r"^ところで",     txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^ところで",       "", txt)
    elif bool(re.search(r"^さて",         txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^さて",           "", txt)
    elif bool(re.search(r"^では",         txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^では",           "", txt)
    elif bool(re.search(r"^時に",         txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^時に",           "", txt)
    elif bool(re.search(r"^ときに",       txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^ときに",         "", txt)
    elif bool(re.search(r"^やがては",     txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^やがては",       "", txt)
    elif bool(re.search(r"^やがて",       txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^やがては",       "", txt)
    elif bool(re.search(r"^それでは", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^それでは",       "", txt)
    elif bool(re.search(r"^それじゃあ", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^それじゃあ",     "", txt)
    elif bool(re.search(r"^それじゃ", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^それじゃ",       "", txt)
    elif bool(re.search(r"^では", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^では",           "", txt)
    elif bool(re.search(r"^ひょっとすると", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^ひょっとすると", "", txt)
    elif bool(re.search(r"^もしかすると", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^もしかすると",   "", txt)
    elif bool(re.search(r"^もしかして", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^もしかして",     "", txt)
    elif bool(re.search(r"^もしも", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^もしも",         "", txt)
    elif bool(re.search(r"^どうやって", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^どうやって",     "", txt)
    elif bool(re.search(r"^どうして", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^どうして",       "", txt)
    elif bool(re.search(r"^ではなぜ", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^ではなぜ",       "", txt)
    elif bool(re.search(r"^なぜ", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^なぜ",           "", txt)
    elif bool(re.search(r"^何故に", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^何故に",   "", txt)
    elif bool(re.search(r"^故に", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^故に",   "", txt)
    elif bool(re.search(r"^ゆえに", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^ゆえに",   "", txt)
    elif bool(re.search(r"^何故", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^何故",   "", txt)
    elif bool(re.search(r"^なにゆえ", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^なにゆえ",   "", txt)
    elif bool(re.search(r"^即ち",         txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^即ち",           "", txt)
    elif bool(re.search(r"^すなわち",     txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^すなわち",       "", txt)
    elif bool(re.search(r"^忽ち", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^忽ち",           "", txt)
    elif bool(re.search(r"^たちまち", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^たちまち",       "", txt)
    elif bool(re.search(r"^立ち所に", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^立ち所に",       "", txt)
    elif bool(re.search(r"^立ちどころに", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^立ちどころに",   "", txt)
    elif bool(re.search(r"^又しても", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^又しても",   "", txt)
    elif bool(re.search(r"^またしても", txt)):
         rmvd_1st_cnnct_txt = re.sub(r"^またしても",   "", txt)
    else:
         rmvd_1st_cnnct_txt = txt


    return rmvd_1st_cnnct_txt


#テキストの中に含まれる第二のコネクト(＝体言＆用言＋接続助詞等の形)を除去する
def remove_2nd_connect(txt):
    extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt = extract_2nd_connect(txt)
    txt.strip(extrctd_2nd_cnnct_txt)


    return txt


#テキストの中に含まれる第一のコネクト(＝前文との接続の種類＆類型)を抽出する(接続語等も抽出する)
def extract_1st_connect(txt):
    if   bool(re.search(r"^そうして",       txt)):
         extrctd_1st_cnnct     = "順接"
         extrctd_1st_cnnct_txt = "そうして"
    elif bool(re.search(r"^そして",         txt)):
         extrctd_1st_cnnct     = "順接"
         extrctd_1st_cnnct_txt = "そして"
    elif bool(re.search(r"^それで",         txt)):
         extrctd_1st_cnnct     = "順接"
         extrctd_1st_cnnct_txt = "それで"
    elif bool(re.search(r"^だから",         txt)):
         extrctd_1st_cnnct     = "順接"
         extrctd_1st_cnnct_txt = "だから"
    elif bool(re.search(r"^従って",         txt)):
         extrctd_1st_cnnct     = "順接"
         extrctd_1st_cnnct_txt = "従って"
    elif bool(re.search(r"^したがって",     txt)):
         extrctd_1st_cnnct     = "順接"
         extrctd_1st_cnnct_txt = "したがって"
    elif bool(re.search(r"^なので",         txt)):
         extrctd_1st_cnnct     = "順接"
         extrctd_1st_cnnct_txt = "なので"
    elif bool(re.search(r"^そこで",         txt)):
         extrctd_1st_cnnct     = "順接"
         extrctd_1st_cnnct_txt = "そこで"
    elif bool(re.search(r"^すると",         txt)):
         extrctd_1st_cnnct     = "順接"
         extrctd_1st_cnnct_txt = "すると"
    elif bool(re.search(r"^しかし",         txt)):
         extrctd_1st_cnnct     = "逆接"
         extrctd_1st_cnnct_txt = "しかし"
    elif bool(re.search(r"^だが",           txt)):
         extrctd_1st_cnnct     = "逆接"
         extrctd_1st_cnnct_txt = "だが"
    elif bool(re.search(r"^でも",           txt)):
         extrctd_1st_cnnct     = "逆接"
         extrctd_1st_cnnct_txt = "でも"
    elif bool(re.search(r"^けれども",       txt)):
         extrctd_1st_cnnct     = "逆接"
         extrctd_1st_cnnct_txt = "けれども"
    elif bool(re.search(r"^所が",           txt)):
         extrctd_1st_cnnct     = "逆接"
         extrctd_1st_cnnct_txt = "所が"
    elif bool(re.search(r"^ところが",       txt)):
         extrctd_1st_cnnct     = "逆接"
         extrctd_1st_cnnct_txt = "ところが"
    elif bool(re.search(r"^尚も",           txt)):
         extrctd_1st_cnnct     = "持続＆継続"
         extrctd_1st_cnnct_txt = "尚も"
    elif bool(re.search(r"^なおも",         txt)):
         extrctd_1st_cnnct     = "持続＆継続"
         extrctd_1st_cnnct_txt = "なおも"
    elif bool(re.search(r"^加えれば",       txt)):
         extrctd_1st_cnnct     = "追加＆補足"
         extrctd_1st_cnnct_txt = "加えれば"
    elif bool(re.search(r"^加えると",       txt)):
         extrctd_1st_cnnct     = "追加＆補足"
         extrctd_1st_cnnct_txt = "加えると"
    elif bool(re.search(r"^加えて",         txt)):
         extrctd_1st_cnnct     = "追加＆補足"
         extrctd_1st_cnnct_txt = "加えて"
    elif bool(re.search(r"^あと",           txt)):
         extrctd_1st_cnnct     = "追加＆補足"
         extrctd_1st_cnnct_txt = "あと"
    elif bool(re.search(r"^又",             txt)):
         extrctd_1st_cnnct     = "添加＆補足"
         extrctd_1st_cnnct_txt = "又"
    elif bool(re.search(r"^また",           txt)):
         extrctd_1st_cnnct     = "添加＆補足"
         extrctd_1st_cnnct_txt = "また"
    elif bool(re.search(r"^尚",             txt)):
         extrctd_1st_cnnct     = "添加＆補足"
         extrctd_1st_cnnct_txt = "尚"
    elif bool(re.search(r"^なお",           txt)):
         extrctd_1st_cnnct     = "添加＆補足"
         extrctd_1st_cnnct_txt = "なお"
    elif bool(re.search(r"^又は",           txt)):
         extrctd_1st_cnnct     = "対置＆対立:論理和"
         extrctd_1st_cnnct_txt = "又は"
    elif bool(re.search(r"^または",         txt)):
         extrctd_1st_cnnct     = "対置＆対立:論理和"
         extrctd_1st_cnnct_txt = "または"
    elif bool(re.search(r"^若しくは",       txt)):
         extrctd_1st_cnnct     = "対置＆対立:論理和"
         extrctd_1st_cnnct_txt = "若しくは"
    elif bool(re.search(r"^もしくは",       txt)):
         extrctd_1st_cnnct     = "対置＆対立:論理和"
         extrctd_1st_cnnct_txt = "もしくは"
    elif bool(re.search(r"^それとも",       txt)):
         extrctd_1st_cnnct     = "対置＆対立:論理和"
         extrctd_1st_cnnct_txt = "それとも"
    elif bool(re.search(r"^尚且つ",         txt)):
         extrctd_1st_cnnct     = "並置＆並立:論理積"
         extrctd_1st_cnnct_txt = "尚且つ"
    elif bool(re.search(r"^尚かつ",         txt)):
         extrctd_1st_cnnct     = "並置＆並立:論理積"
         extrctd_1st_cnnct_txt = "尚かつ"
    elif bool(re.search(r"^なおかつ",       txt)):
         extrctd_1st_cnnct     = "並置＆並立:論理積"
         extrctd_1st_cnnct_txt = "なおかつ"
    elif bool(re.search(r"^且つ",           txt)):
         extrctd_1st_cnnct     = "並置＆並立:論理積"
         extrctd_1st_cnnct_txt = "且つ"
    elif bool(re.search(r"^かつ",           txt)):
         extrctd_1st_cnnct     = "並置＆並立:論理積"
         extrctd_1st_cnnct_txt = "かつ"
    elif bool(re.search(r"^詰まりは",       txt)):
         extrctd_1st_cnnct     = "説明:内容について"
         extrctd_1st_cnnct_txt = "詰まりは"
    elif bool(re.search(r"^つまりは",       txt)):
         extrctd_1st_cnnct     = "説明:内容について"
         extrctd_1st_cnnct_txt = "つまりは"
    elif bool(re.search(r"^詰まり",         txt)):
         extrctd_1st_cnnct     = "説明:内容について"
         extrctd_1st_cnnct_txt = "詰まり"
    elif bool(re.search(r"^つまり",         txt)):
         extrctd_1st_cnnct     = "説明:内容について"
         extrctd_1st_cnnct_txt = "つまり"
    elif bool(re.search(r"^何故ならば",     txt)):
         extrctd_1st_cnnct     = "説明:事由＆理由について"
         extrctd_1st_cnnct_txt = "何故ならば"
    elif bool(re.search(r"^なぜならば",     txt)):
         extrctd_1st_cnnct     = "説明:事由＆理由について"
         extrctd_1st_cnnct_txt = "なぜならば"
    elif bool(re.search(r"^何故なら",       txt)):
         extrctd_1st_cnnct     = "説明:事由＆理由について"
         extrctd_1st_cnnct_txt = "何故なら"
    elif bool(re.search(r"^なぜなら",       txt)):
         extrctd_1st_cnnct     = "説明:事由＆理由について"
         extrctd_1st_cnnct_txt = "なぜなら"
    elif bool(re.search(r"^所で",           txt)):
         extrctd_1st_cnnct     = "転換＆切替"
         extrctd_1st_cnnct_txt = "所で"
    elif bool(re.search(r"^ところで",       txt)):
         extrctd_1st_cnnct     = "転換＆切替"
         extrctd_1st_cnnct_txt = "ところで"
    elif bool(re.search(r"^さて",           txt)):
         extrctd_1st_cnnct     = "転換＆切替"
         extrctd_1st_cnnct_txt = "さて"
    elif bool(re.search(r"^では",           txt)):
         extrctd_1st_cnnct     = "転換＆切替"
         extrctd_1st_cnnct_txt = "では"
    elif bool(re.search(r"^時に",           txt)):
         extrctd_1st_cnnct     = "転換＆切替"
         extrctd_1st_cnnct_txt = "時に"
    elif bool(re.search(r"^ときに",         txt)):
         extrctd_1st_cnnct     = "転換＆切替"
         extrctd_1st_cnnct_txt = "ときに"
    elif bool(re.search(r"^やがては",       txt)):
         extrctd_1st_cnnct     = "展開＆発展"
         extrctd_1st_cnnct_txt = "やがては"
    elif bool(re.search(r"^やがて",     txt)):
         extrctd_1st_cnnct     = "展開＆発展"
         extrctd_1st_cnnct_txt = "やがて"
    elif bool(re.search(r"^それでは",       txt)):
         extrctd_1st_cnnct     = "展開＆発展"
         extrctd_1st_cnnct_txt = "それじゃあ"
    elif bool(re.search(r"^それじゃあ",     txt)):
         extrctd_1st_cnnct     = "展開＆発展"
         extrctd_1st_cnnct_txt = "それじゃ"
    elif bool(re.search(r"^それじゃ",       txt)):
         extrctd_1st_cnnct     = "展開＆発展"
         extrctd_1st_cnnct_txt = "それでは"
    elif bool(re.search(r"^では",           txt)):
         extrctd_1st_cnnct     = "展開＆発展"
         extrctd_1st_cnnct_txt = "では"
    elif bool(re.search(r"^ひょっとすると", txt)):
         extrctd_1st_cnnct     = "仮定＆仮説"
         extrctd_1st_cnnct_txt = "ひょっとすると"
    elif bool(re.search(r"^もしかすると",   txt)):
         extrctd_1st_cnnct     = "仮定＆仮説"
         extrctd_1st_cnnct_txt = "もしかすると"
    elif bool(re.search(r"^もしかして",     txt)):
         extrctd_1st_cnnct     = "仮定＆仮説"
         extrctd_1st_cnnct_txt = "もしかして"
    elif bool(re.search(r"^もしも",         txt)):
         extrctd_1st_cnnct     = "仮定＆仮説"
         extrctd_1st_cnnct_txt = "もしも"
    elif bool(re.search(r"^どうやって", txt)):
         extrctd_1st_cnnct     = "疑義＆質問＆確認:手段＆方法について"
         extrctd_1st_cnnct_txt = "どうやって"
    elif bool(re.search(r"^どうして", txt)):
         extrctd_1st_cnnct     = "疑義＆質問＆確認:事由＆理由について"
         extrctd_1st_cnnct_txt = "どうして"
    elif bool(re.search(r"^ではなぜ", txt)):
         extrctd_1st_cnnct     = "疑義＆質問＆確認:事由＆理由について"
         extrctd_1st_cnnct_txt = "ではなぜ"
    elif bool(re.search(r"^なぜ", txt)):
         extrctd_1st_cnnct     = "疑義＆質問＆確認:事由＆理由について"
         extrctd_1st_cnnct_txt = "なぜ"
    elif bool(re.search(r"^何故に", txt)):
         extrctd_1st_cnnct     = "疑義＆質問＆確認:事由＆理由について"
         extrctd_1st_cnnct_txt = "何故に"
    elif bool(re.search(r"^何故", txt)):
         extrctd_1st_cnnct     = "疑義＆質問＆確認:事由＆理由について"
         extrctd_1st_cnnct_txt = "何故"
    elif bool(re.search(r"^故に", txt)):
         extrctd_1st_cnnct     = "疑義＆質問＆確認:事由＆理由について"
         extrctd_1st_cnnct_txt = "故に"
    elif bool(re.search(r"^ゆえに", txt)):
         extrctd_1st_cnnct     = "疑義＆質問＆確認:事由＆理由について"
         extrctd_1st_cnnct_txt = "ゆえに"
    elif bool(re.search(r"^なにゆえ", txt)):
         extrctd_1st_cnnct     = "疑義＆質問＆確認:事由＆理由について"
         extrctd_1st_cnnct_txt = "なにゆえ"
    elif bool(re.search(r"^即ち", txt)):
         extrctd_1st_cnnct     = "当意＆帰結"
         extrctd_1st_cnnct_txt = "即ち"
    elif bool(re.search(r"^すなわち", txt)):
         extrctd_1st_cnnct     = "当意＆帰結"
         extrctd_1st_cnnct_txt = "すなわち"
    elif bool(re.search(r"^忽ち", txt)):
         extrctd_1st_cnnct     = "加速度的発展・転回:やや順接的"
         extrctd_1st_cnnct_txt = "忽ち"
    elif bool(re.search(r"^たちまち", txt)):
         extrctd_1st_cnnct     = "加速度的発展・転回:やや順接的"
         extrctd_1st_cnnct_txt = "たちまち"
    elif bool(re.search(r"^立ち所に", txt)):
         extrctd_1st_cnnct     = "加速度的発展・転回:やや逆接的"
         extrctd_1st_cnnct_txt = "立ち所に"
    elif bool(re.search(r"^立ちどころに", txt)):
         extrctd_1st_cnnct     = "加速度的発展・転回:やや逆接的"
         extrctd_1st_cnnct_txt = "立ちどころに"
    elif bool(re.search(r"^又しても", txt)):
         extrctd_1st_cnnct     = "再度＆繰返し"
         extrctd_1st_cnnct_txt = "又しても"
    elif bool(re.search(r"^またしても", txt)):
         extrctd_1st_cnnct     = "再度＆繰返し"
         extrctd_1st_cnnct_txt = "またしても"
    else:
           extrctd_1st_cnnct     = "無し"
           extrctd_1st_cnnct_txt = "無し"


    return extrctd_1st_cnnct, extrctd_1st_cnnct_txt


#テキストの中に含まれる第二のコネクト(＝体言＆用言＋接続助詞等の形)を抽出する
def extract_2nd_connect(txt):
    txt_tkns           = []
    anlyzd_txt            = ""
    extrctd_2nd_cnnct     = ""
    extrctd_2nd_cnnct_txt = ""
    tkns_seq              = ""
    tkns_idx              = 0
    tkns_idx2             = 0
    itr_end               = 0


    rmvd_symbl_txt     = remove_symbols(txt)
    rmvd_emoji_txt     = remove_emoji(rmvd_symbl_txt)
    rmvd_emotnl_txt    = remove_emotional(rmvd_emoji_txt)
    rmvd_fnl_prtcl_txt = remove_final_particle(rmvd_emotnl_txt)
    rmvd_1st_cnnct_txt = remove_1st_connect(rmvd_fnl_prtcl_txt)
    extrctd_cntnt_txt  = rmvd_1st_cnnct_txt

    tkns  = token_analyze2(extrctd_cntnt_txt)

    tkns = join_tokens_by_noun(tkns)
    tkns = join_tokens_by_noun_between_jp_no(tkns)
    tkns = join_tokens_by_verb_and_auxiliary_verb(tkns)
    tkns = join_tokens_by_verbs_and_conjunctive_particle(tkns)
    tkns = join_tokens_by_verbs_conjunctive_particle_and_verbs(tkns)
    tkns = join_tokens_by_jp_to_as_case_particle_and_jp_ha_as_participant_particle(tkns)


    while tkns_idx < len(tkns):

          if "すれば" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "すれば系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "しては" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "しては系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "しても" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "しても系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "して" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "して系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "だとしては" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "だとしては系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "としては" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "としては系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "だとしても" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "だとしても系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "としても" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "としても系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "として" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "として系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "たらば" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "たらば系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "たら" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "たら系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "だとしては" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "だとしては系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "としては" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "としては系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "だとしても" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "だとしても系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "としても" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "としても系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "として" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "として系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "ではあっても" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "ではあっても系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "ではなくても" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "ではなくても系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "ではなくとも" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "ではなくとも系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "であっても" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "であっても系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "でなくても" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "でなくても系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "でなくとも" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "でなくとも系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "でも" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "でも系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "ではあるので" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "ではあるので系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "ではないので" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "ではないので系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "であるので" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "であるので系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "でないので" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "でないので系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "なので" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "なので系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "ので" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "ので系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "したから" in tkns[tkns_idx][0]:
              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "したから系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "したけれども" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "したけれども系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "したけれど" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "したけれど系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "したけど" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "したけど系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "だけど" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "だけど系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "いけど" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "いけど系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "であるならば" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "であるならば系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "でないならば" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "でないならば系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "であるなら" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "であるなら系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "でないなら" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "でないなら系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "なら" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "なら系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "であるが" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "であるが系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "だが" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "だが系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "ではないが" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "ではないが系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "でないが" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "でないが系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "はあるが" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "はあるが系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "はないが" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "でないが系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "はあるけれども" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "はあるけれども系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "はないけれども" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "はないけれども系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt

          if "はあるけれど" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "はあるけれど系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "はないけれど" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "はないけれど系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "に対しては" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "に対しては"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "に対しても" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "に対しても系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "に対して" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "に対して系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "にとっては" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "にとっては系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "にとっても" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "にとっても系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "にとって" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "にとって系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "においては" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "においては系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "においても" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "においても系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "において" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "において系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "については" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "については系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "についても" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "についても系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "について" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "について系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "におかれましては" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "におかれましては系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "におかれましても" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "におかれましても系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "におかれては" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "におかれては系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          if "におかれても" in tkns[tkns_idx][0]:

              itr_end  = tkns_idx

              while tkns_idx2 <= itr_end:
                    tkns_seq += tkns[tkns_idx2][0]
                    tkns_idx2 += 1
              else:
                    tkns_idx2 = 0

          if tkns_seq != "":
             extrctd_2nd_cnnct     = "におかれても系"
             extrctd_2nd_cnnct_txt = tkns_seq
             
             return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


          tkns_idx += 1

    else:

          extrctd_2nd_cnnct = "不明・その他"

          while tkns_idx2 < len(tkns):
                txt_tkns.append(tkns[tkns_idx2][0])
                tkns_idx2 += 1

          for anlyzd_tkn in txt_tkns:
              anlyzd_txt += anlyzd_tkn

          extrctd_2nd_cnnct_txt = anlyzd_txt


          return extrctd_2nd_cnnct, extrctd_2nd_cnnct_txt


#テキストがギャグ＆声帯模写だったとして、それらからインテント(＝発話の意図＆種類＆類型)を抽出する
def extract_intent_from_gag_and_vocal_cord_copy(txt):
    if   (txt == "はい ひょっこりはん" or
          txt == "はい ひょっこりはん！" or
          txt == "はいひょっこりはん" or
          txt == "はいひょっこりはん！" or
          txt == "プレゼント フォー 肩幅" or
          txt == "プレゼント フォー 肩幅！" or
          txt == "プレゼントフォー肩幅" or
          txt == "プレゼントフォー肩幅！" or
          txt == "うぃーん合唱団" or
          txt == "うぃーん合唱団！" or
          txt == "早く大人になれ 膝小僧" or
          txt == "早く大人になれ 膝小僧！" or
          txt == "早く大人になれ膝小僧" or
          txt == "早く大人になれ膝小僧！" or
          txt == "おったまげ" or
          txt == "おったまげ！" or
          txt == "おったまげー" or
          txt == "おったまげー！" or
          txt == "おったまげ～" or
          txt == "おったまげ～！" or
          txt == "しもしも" or
          txt == "しもしも？" or
          txt == "マンモスうれぴー" or
          txt == "マンモスうれぴー！" or
          txt == "マンモスうれぴ～" or
          txt == "マンモスうれぴ～！" or
          txt == "湯飲みじゃなくて,ホタルを守る" or
          txt == "湯飲みじゃなくてホタルを守る" or
          txt == "ウーパールーパー" or
          txt == "ウーパールーパー！" or
          txt == "スフィンクス" or
          txt == "スフィンクス！" or
          txt == "しゃか" or
          txt == "しゃか！" or
          txt == "ホップステップ キャンプ" or
          txt == "ホップステップ キャンプ！" or
          txt == "ホップステップキャンプ" or
          txt == "ホップステップキャンプ！" or
          txt == "落ち着いていきや" or
          txt == "落ち着いていきや！" or
          txt == "落ち着いていきやー" or
          txt == "落ち着いていきやー！" or
          txt == "落ち着いていきや～" or
          txt == "落ち着いていきや～！" or
          txt == "PPAP" or
          txt == "PPAP!" or
          txt == "PPAP！" or
          txt == "パーフェクト ヒューマン" or
          txt == "パーフェクト ヒューマン！" or
          txt == "パーフェクトヒューマン" or
          txt == "パーフェクトヒューマン！" or
          txt == "ボク ミッキーだよ" or
          txt == "ボク ミッキーだよ！" or
          txt == "ボクミッキーだよ" or
          txt == "ボクミッキーだよ！" or
          txt == "あのね 芦田愛菜だよ" or
          txt == "あのね 芦田愛菜だよ！" or
          txt == "あのね芦田愛菜だよ" or
          txt == "あのね芦田愛菜だよ！" or
          txt == "ピカピカ" or
          txt == "ピカピカ！" or
          txt == "ピカチュウ" or
          txt == "ピカチュウ！" or
          txt == "ブンブン ハローYouTube" or
          txt == "ブンブン ハローYouTube!" or
          txt == "ブンブンハローYouTube" or
          txt == "ブンブンハローYouTube!" or
          txt == "ブンブン ハロー" or
          txt == "ブンブン ハロー！" or
          txt == "ブンブンハロー" or
          txt == "ブンブンハロー！" or
          txt == "ぶんぶん はろー" or
          txt == "ぶんぶん はろー！" or
          txt == "ぶんぶんはろー" or
          txt == "ぶんぶんはろー！" or
          txt == "ダンカン コノヤロ！" or
          txt == "ダンカンコノヤロ！" or
          txt == "大阪名物 パチパチパンチ" or
          txt == "大阪名物 パチパチパンチ！" or
          txt == "大阪名物パチパチパンチ" or
          txt == "大阪名物パチパチパンチ！" or
          txt == "パチパチパンチ" or
          txt == "パチパチパンチ！" or
          txt == "かいーの" or
          txt == "かいーの！" or
          txt == "かい～の" or
          txt == "かい～の！" or
          txt == "かいーのー" or
          txt == "かいーのー！" or
          txt == "かい～の～" or
          txt == "かい～の～！" or
          txt == "バカちゃいまんねん アホでんねん" or
          txt == "バカちゃいまんねん アホでんねん！" or
          txt == "バカちゃいまんねんアホでんねん" or
          txt == "バカちゃいまんねんアホでんねん！" or
          txt == "アホでんねん" or
          txt == "アホでんねん！" or
          txt == "おっぱっぴー" or
          txt == "おっぱっぴー！" or
          txt == "オッパッピー" or
          txt == "オッパッピー！" or
          txt == "おっぱっぴ～" or
          txt == "おっぱっぴ～！" or
          txt == "オッパッピ～" or
          txt == "オッパッピ～！" or
          txt == "ぴぃやー" or
          txt == "ぴぃやー！" or
          txt == "ピィヤー" or
          txt == "ピィヤー！" or
          txt == "ぴぃや～" or
          txt == "ぴぃや～！" or
          txt == "ピィヤ～" or
          txt == "ピィヤ～！" or
          txt == "俺の武勇伝" or
          txt == "俺の武勇伝！" or
          txt == "おれの武勇伝" or
          txt == "おれの武勇伝！" or
          txt == "オレの武勇伝" or
          txt == "オレの武勇伝！" or
          txt == "武勇伝" or
          txt == "武勇伝！" or
          txt == "俺の武勇伝を聞きたいか" or
          txt == "おれの武勇伝を聞きたいか" or
          txt == "オレの武勇伝を聞きたいか" or
          txt == "俺の武勇伝を聞きたいか？" or
          txt == "おれの武勇伝を聞きたいか？" or
          txt == "オレの武勇伝を聞きたいか？" or
          txt == "武勇伝 武勇伝" or
          txt == "武勇伝武勇伝" or
          txt == "キミ カワイーね" or
          txt == "キミカワイーね" or
          txt == "空前絶後" or
          txt == "空 前 絶 後" or
          txt == "空！ 前！ 絶！ 後！" or
          txt == "空！前！絶！後！" or
          txt == "失礼 ぶっこきました" or
          txt == "失礼ぶっこきました"):
           extrctd_intnt = "モノマネ＆ギャグ＆一発芸:人物やキャラクターに基づいて"
    elif (txt == "にゃー にゃー" or
          txt == "にゃーにゃー" or
          txt == "ニャー ニャー" or
          txt == "ニャーニャー" or
          txt == "にゃ" or
          txt == "ニャ" or
          txt == "にゃー" or
          txt == "ニャー" or
          txt == "にゃ～" or
          txt == "ニャ～" or
          txt == "わんわん" or
          txt == "ワンワン" or
          txt == "わん" or
          txt == "ワン" or
          txt == "しゃー" or
          txt == "シャー" or
          txt == "ぎゃん ぎゃん" or
          txt == "ぎゃんぎゃん" or
          txt == "ギャン ギャン" or
          txt == "ギャンギャン" or
          txt == "ぎゃん" or
          txt == "ギャン" or
          txt == "うほ うほ" or         
          txt == "うほうほ" or
          txt == "ウホ ウホ" or
          txt == "ウホウホ" or
          txt == "うほ" or
          txt == "ウホ" or
          txt == "こけこっこー" or
          txt == "コケコッコー" or
          txt == "こけ" or
          txt == "コケ" or
          txt == "がお がおー" or
          txt == "がおがおー" or
          txt == "ガオ ガオー" or
          txt == "ガオガオー" or
          txt == "がおー" or
          txt == "ガオー" or
          txt == "ぶひ ぶひ" or
          txt == "ぶひぶひ" or
          txt == "ブヒ ブヒ" or
          txt == "ブヒブヒ" or
          txt == "ぶひ" or
          txt == "ブヒ" or
          txt == "ちゅん ちゅん" or
          txt == "ちゅんちゅん" or
          txt == "チュン チュン" or
          txt == "チュンチュン" or
          txt == "ちゅん" or
          txt == "チュン" or
          txt == "げろ げろ" or
          txt == "げろげろ" or
          txt == "ゲロ ゲロ" or
          txt == "ゲロゲロ" or
          txt == "げろ" or
          txt == "ゲロ" or
          txt == "げこ げこ" or
          txt == "げこげこ" or
          txt == "ゲコ ゲコ" or
          txt == "ゲコゲコ" or
          txt == "げこ" or
          txt == "ゲコ" or
          txt == "ぶー ぶー" or
          txt == "ぶーぶー" or
          txt == "ブー ブー" or
          txt == "ブーブー" or
          txt == "がったん ごっとん" or
          txt == "がったんごっとん" or
          txt == "ガッタン ゴットン" or
          txt == "ガッタンゴットン"):
           extrctd_intnt = "モノマネ＆声帯模写:擬音や擬態語"
    elif (txt == "ぷー" or
          txt == "プー" or
          txt == "ぷ～" or
          txt == "プ～" or
          txt == "ぶりぶり" or
          txt == "ブリブリ" or
          txt == "ごほ ごほ" or
          txt == "ごほごほ" or
          txt == "ゴホ ゴホ" or
          txt == "ゴホゴホ" or
          txt == "ごほ" or
          txt == "ゴホ" or
          txt == "ごほっ ごほっ" or
          txt == "ごほっごほっ" or
          txt == "ゴホッ ゴホッ" or
          txt == "ゴホッゴホッ" or
          txt == "ごほっ" or
          txt == "ゴホッ" or
          txt == "へぶし" or
          txt == "ヘブシ" or
          txt == "へぶしっ" or
          txt == "ヘブシッ" or
          txt == "はっくしょん" or
          txt == "ハックション"):
           extrctd_intnt = "生理現象:擬音や擬態語"
    elif (txt == "ブー ブー" or
          txt == "ブーブー" or
          txt == "ブー！ ブー！" or
          txt == "ブー！ブー！"):
           extrctd_intnt = "ブーイング"
    elif (txt == "ああ" or
          txt == "ええ" or
          txt == "おお" or
          txt == "うん"):
           extrctd_intnt = "相槌:生返事に近い"
    elif (txt == "あのー" or
          txt == "あの～" or
          txt == "あー" or
          txt == "あ～" or
          txt == "えーと" or
          txt == "え～と" or
          txt == "えー" or
          txt == "え～" or
          txt == "うーん" or
          txt == "う～ん" or
          txt == "うー" or
          txt == "う～"):
           extrctd_intnt = "フィラー:間の引き延ばし"
    elif (txt == "海" or
          txt == "海！" or
          txt == "うみ" or
          txt == "うみ！" or
          txt == "セイ イェーイ" or
          txt == "セイ イェーイ！" or
          txt == "セイイェーイ" or 
          txt == "セイイェーイ！"):
           extrctd_intnt = "掛合い＝コールアンドレスポンス"
    else:
           extrctd_intnt = "不明・その他"

    return extrctd_intnt


#テキストが短文＆定型文だったとして、それらからインテント(＝発話の意図＆種類＆類型)を抽出する(主として、子供や児童に向けられる言葉)
def extract_intent_from_short_and_boilerplate_for_child(txt):
    if   (txt == "良く頑張ったわね" or
          txt == "よく頑張ったわね" or
          txt == "よくがんばったわね" or
          txt == "良く頑張ったね" or
          txt == "よく頑張ったね" or
          txt == "よくがんばったね" or
          txt == "良く頑張ったな" or
          txt == "よく頑張ったな" or
          txt == "よくがんばったな" or
          txt == "良く頑張った" or
          txt == "よく頑張った" or
          txt == "よくがんばった" or
          txt == "頑張ったわね" or
          txt == "がんばったわね" or
          txt == "頑張ったね" or
          txt == "がんばったね"):
           extrctd_intnt = "慰労:やや上の立場や目線から"
    elif (txt == "これからも頑張ってね" or
          txt == "これからもがんばってね" or
          txt == "これからも頑張って" or
          txt == "これからもがんばって" or
          txt == "これからも頑張れ" or
          txt == "これからもがんばれ" or
          txt == "次からも頑張ってね" or
          txt == "次からもがんばってね" or
          txt == "次からも頑張って" or
          txt == "次からもがんばって" or
          txt == "次からも頑張れ" or
          txt == "次からもがんばれ" or
          txt == "次も頑張ってね" or
          txt == "次もがんばってね" or
          txt == "次も頑張って" or
          txt == "次もがんばって" or
          txt == "次も頑張れ" or
          txt == "次もがんばれ"):
           extrctd_intnt = "激励:やや上の立場や目線から"
    elif (txt == "凄いわね" or
          txt == "すごいわね" or
          txt == "凄いね" or
          txt == "すごいね" or
          txt == "凄いぞ" or
          txt == "すごいぞ" or
          txt == "凄いな" or
          txt == "すごいな"):
           extrctd_intnt = "賞賛:やや上の立場や目線から"
    elif (txt == "有り難うね" or
          txt == "ありがとうね" or
          txt == "有り難ね" or
          txt == "ありがとね" or
          txt == "いつも有り難うね" or
          txt == "いつもありがとうね" or
          txt == "いつも有り難ね" or
          txt == "いつもありがとね"):
           extrctd_intnt = "感謝:やや上の立場や目線から"
    elif (txt == "おめでとうね" or
          txt == "おめでとう" or
          txt == "おめでと"):
           extrctd_intnt = "祝福:やや上の立場や目線から"
    elif (txt == "良い子だわ" or
          txt == "よい子だわ" or
          txt == "良い子だね" or
          txt == "よい子だね" or
          txt == "良い子だぞ" or
          txt == "よい子だぞ" or
          txt == "良い子だな" or
          txt == "よい子だな" or
          txt == "良い子だ" or
          txt == "よい子だ" or
          txt == "良い子 良い子" or
          txt == "よい子 よい子"):
           extrctd_intnt = "褒め:性格や人格面について,やや上の立場や目線から"
    elif (txt == "賢いわね" or
          txt == "賢いね" or
          txt == "かしこいね" or
          txt == "賢いぞ" or
          txt == "かしこいぞ" or
          txt == "賢いな" or
          txt == "かしこい" or
          txt == "天才だわ" or
          txt == "天才ね" or
          txt == "天才だぞ" or
          txt == "天才だな" or
          txt == "天才だ"):
           extrctd_intnt = "褒め:知性や知力について,やや上の立場や目線から"
    elif (txt == "上手になったわね" or
          txt == "上手になったね" or
          txt == "上手になったぞ" or
          txt == "上手になったな" or
          txt == "上手になった" or
          txt == "上達したわね" or
          txt == "上達したね" or
          txt == "上達したぞ" or
          txt == "上達したな"):
           extrctd_intnt = "褒め:芸事や習い事について,やや上の立場や目線から"
    elif (txt == "成長したわね" or
          txt == "成長したね" or
          txt == "成長したな"):
           extrctd_intnt = "褒め:身体や精神面について,やや上の立場や目線から"
    elif (txt == "成長したわね" or
          txt == "成長したね" or
          txt == "成長したな"):
           extrctd_intnt = "褒め:身体や精神面について,やや上の立場や目線から"
    elif (txt == "偉いわね" or
          txt == "成長したね" or
          txt == "成長したな"):
           extrctd_intnt = "褒め:身体や精神面について,やや上の立場や目線から"
    else:
           extrctd_intnt = "不明・その他"

    return extrctd_intnt


#テキストが短文＆定型文だったとして、それらからインテント(＝発話の意図＆種類＆類型)を抽出する(主として、成人や大人に向けられる言葉)
def extract_intent_from_short_and_boilerplate_for_adlut(txt):
    if   (txt == "お初にお目にかかります" or
          txt == "初めまして" or
          txt == "はじめまして"):
           extrctd_intnt = "挨拶:初対面・顔合わせの際のもの"
    elif (txt == "やあ" or
          txt == "どうも" or
          txt == "御免遊ばせ" or
          txt == "御免あそばせ" or
          txt == "ごめん遊ばせ" or
          txt == "ごめんあそばせ" or
          txt == "おはよう御座います" or
          txt == "おはようございます" or
          txt == "おはよう♪" or
          txt == "おはよう！" or
          txt == "おはよう" or
          txt == "おはっす" or
          txt == "おは" or
          txt == "こんにちは" or
          txt == "こんにちわ" or
          txt == "ちはっす" or
          txt == "ちわっす" or
          txt == "こんばんは" or
          txt == "こんばんわ" or
          txt == "ばんわ" or
          txt == "ばんは" or
          txt == "ばんっす" or
          txt == "ばん"):
           extrctd_intnt = "挨拶:時間帯によるもの"
    elif (txt == "お先に失礼します" or
          txt == "それでは失礼します" or
          txt == "失礼します" or
          txt == "さようなら" or
          txt == "サヨウナラ" or
          txt == "サヨナラ" or
          txt == "また明日"):
           extrctd_intnt = "挨拶:会社や学校などで"
    elif (txt == "行って参ります" or
          txt == "行ってまいります" or
          txt == "行ってきます" or
          txt == "行きます" or
          txt == "行く"):
           extrctd_intnt = "常套句＆決まり文句:自宅や会社から出る際のもの"
    elif (txt == "只今戻りました" or
          txt == "ただいま戻りました" or
          txt == "只今" or
          txt == "ただいま" or
          txt == "お帰りなさいませ" or
          txt == "おかえりなさいませ" or
          txt == "お帰りなさい" or
          txt == "おかえりなさい"):
           extrctd_intnt = "常套句＆決まり文句:自宅や会社に戻る際のもの"
    elif (txt == "少々 お待ち下さい" or
          txt == "少々 お待ちください" or
          txt == "少々お待ち下さい" or
          txt == "少々お待ちください" or
          txt == "少し 待って下さい" or
          txt == "少し 待ってください" or
          txt == "少し待って下さい" or
          txt == "少し待ってください" or
          txt == "ちょっと待って" or
          txt == "チョット待って"):
           extrctd_intnt = "常套句＆決まり文句:相手を待たせる際のもの"
    elif (txt == "待っていました" or
          txt == "待ってました" or
          txt == "待ってた"):
           extrctd_intnt = "常套句＆決まり文句:相手に待たされた際のもの"
    elif (txt == "以後気を付けて下さい" or
          txt == "以後気を付けてください" or
          txt == "気を付けて下さい" or
          txt == "気を付けてください" or
          txt == "気をつけろ" or
          txt == "しっかりしろ" or
          txt == "しっかりやれ" or
          txt == "こら" or
          txt == "コラ"):
           extrctd_intnt = "注意＆叱責"
    elif (txt == "以後気を付けます" or
          txt == "気を付けます" or
          txt == "気をつけます" or
          txt == "しっかりします" or
          txt == "しっかりやります"):
           extrctd_intnt = "常套句＆決まり文句:注意や叱責された際のもの"
    elif (txt == "失礼ですが" or
          txt == "失礼" or
          txt == "すみません" or
          txt == "すいません" or
          txt == "おい" or
          txt == "ねえ" or
          txt == "ねぇ" or
          txt == "なあ" or
          txt == "なぁ"):
           extrctd_intnt = "呼掛け＆問掛け"
    elif (txt == "流石ですね" or
          txt == "流石です" or
          txt == "流石ね" or
          txt == "流石" or
          txt == "さすがですね" or
          txt == "さすがです" or
          txt == "さすがね" or
          txt == "さすが" or
          txt == "凄いですね" or
          txt == "凄いです" or
          txt == "凄いね" or
          txt == "凄い" or
          txt == "すごいですね" or
          txt == "すごいです" or
          txt == "すごいね" or
          txt == "すごい" or
          txt == "素晴らしいですね" or
          txt == "すばらしいですね" or
          txt == "素晴らしいです" or
          txt == "すばらしいです" or
          txt == "素晴らしい" or
          txt == "すばらしい" or
          txt == "賢いですね" or
          txt == "賢いです" or
          txt == "賢いね" or
          txt == "賢い" or
          txt == "偉いですね" or
          txt == "偉いです" or
          txt == "偉いね" or
          txt == "偉い" or
          txt == "エラいですね" or
          txt == "エラいです" or
          txt == "エラいね" or
          txt == "エラい" or
          txt == "立派ですね" or
          txt == "立派です" or
          txt == "立派ね" or
          txt == "立派" or
          txt == "感服しました" or
          txt == "感服したわ" or
          txt == "感服した" or
          txt == "敬服いたします" or
          txt == "敬服しますわ" or
          txt == "敬服します" or
          txt == "感動しました" or
          txt == "感動したわ" or
          txt == "感動した" or
          txt == "かっこいいですね" or
          txt == "カッコいいですね" or
          txt == "カッコイイですね" or
          txt == "かっこいいです" or
          txt == "カッコいいです" or
          txt == "カッコイイです" or
          txt == "かっこいいわね" or
          txt == "カッコいいわね" or
          txt == "カッコイイわね" or
          txt == "かっこいい" or
          txt == "カッコいい" or
          txt == "カッコイイ" or
          txt == "可愛いですね" or
          txt == "かわいいですね" or
          txt == "カワイいですね" or
          txt == "カワイイですね" or
          txt == "可愛いです" or
          txt == "かわいいです" or
          txt == "カワイいです" or
          txt == "カワイイです" or
          txt == "可愛いわね" or
          txt == "かわいいわね" or
          txt == "カワイいわね" or
          txt == "カワイイわね" or
          txt == "可愛いね" or
          txt == "かわいいね" or
          txt == "カワイいね" or
          txt == "カワイイね" or
          txt == "可愛い" or
          txt == "かわいい" or
          txt == "カワイい" or
          txt == "カワイイ" or
          txt == "かわい" or
          txt == "カワイ" or
          txt == "かわゆす" or
          txt == "カワゆす" or
          txt == "カワユス" or
          txt == "美しいですね" or
          txt == "うつくしいですね" or
          txt == "美しいです" or
          txt == "うつくしいです" or
          txt == "美しいわね" or
          txt == "うつくしいわね" or
          txt == "美しいわ" or
          txt == "うつくしいわ" or
          txt == "美しい" or
          txt == "うつくしい" or
          txt == "綺麗ですね" or
          txt == "きれいですね" or
          txt == "キレいですね" or
          txt == "キレイですね" or
          txt == "綺麗だわ" or
          txt == "きれいだわ" or
          txt == "キレいだわ" or
          txt == "キレイだわ" or
          txt == "綺麗だ" or
          txt == "きれいだ" or
          txt == "キレいだ" or
          txt == "キレイだ" or
          txt == "綺麗ね" or
          txt == "きれいね" or
          txt == "キレいね" or
          txt == "キレイね" or
          txt == "綺麗" or
          txt == "きれい" or
          txt == "キレい" or
          txt == "キレイ" or
          txt == "いけてるよ" or
          txt == "イケてるよ" or
          txt == "イケテルよ" or
          txt == "いけてるね" or
          txt == "イケてるね" or
          txt == "イケテルね" or
          txt == "いけてるな" or
          txt == "イケてるな" or
          txt == "イケテルな" or
          txt == "いけてるわ" or
          txt == "イケてるわ" or
          txt == "イケテルわ" or
          txt == "いけてる" or
          txt == "イケてる" or
          txt == "イケテル" or
          txt == "素敵ですよ" or
          txt == "すてきですよ" or
          txt == "ステキですよ" or
          txt == "素敵ですね" or
          txt == "すてきですね" or
          txt == "ステキですね" or
          txt == "素敵です" or
          txt == "すてきです" or
          txt == "ステキです" or
          txt == "素敵だわ" or
          txt == "すてきだわ" or
          txt == "ステキだわ" or
          txt == "素敵よ" or
          txt == "すてきよ" or
          txt == "ステキよ" or
          txt == "素敵ね" or
          txt == "すてきね" or
          txt == "ステキね" or
          txt == "素敵" or
          txt == "すてき" or
          txt == "ステキ"):
           extrctd_intnt = "称賛＆礼賛:お世辞に近い"
    elif (txt == "この変態め" or
          txt == "このへんたいめ" or
          txt == "このヘンタイめ" or
          txt == "この変態が" or
          txt == "このへんたいが" or
          txt == "このヘンタイが" or
          txt == "変態め" or
          txt == "へんたいめ" or
          txt == "ヘンタイめ" or
          txt == "変態が" or
          txt == "へんたいが" or
          txt == "ヘンタイが" or
          txt == "変態ですね" or
          txt == "へんたいですね" or
          txt == "ヘンタイですね" or
          txt == "変態だわ" or
          txt == "へんたいだわ" or
          txt == "ヘンタイだわ" or
          txt == "変態ね" or
          txt == "へんたいね" or
          txt == "ヘンタイね" or
          txt == "変態" or
          txt == "へんたい" or
          txt == "ヘンタイ" or
          txt == "このぶすめ" or
          txt == "このブスめ" or
          txt == "この不細工め" or
          txt == "このぶさいくめ" or
          txt == "このブサイクめ" or
          txt == "このぶすが" or
          txt == "このブスが" or
          txt == "この不細工が" or
          txt == "このぶさいくが" or
          txt == "このブサイクが" or
          txt == "ぶすめ" or
          txt == "ブスめ" or
          txt == "不細工め" or
          txt == "ぶさいくめ" or
          txt == "ブサイクめ" or
          txt == "ぶすが" or
          txt == "ブスが" or
          txt == "不細工が" or
          txt == "ぶさいくが" or
          txt == "ブサイクが" or
          txt == "ぶすですね" or
          txt == "ブスですね" or
          txt == "不細工ですね" or
          txt == "ぶさいくですね" or
          txt == "ブサイクですね" or
          txt == "ぶすだわ" or
          txt == "ブスだわ" or
          txt == "不細工だわ" or
          txt == "ぶさいくだわ" or
          txt == "ブサイクだわ" or
          txt == "ぶすね" or
          txt == "ブスね" or
          txt == "不細工ね" or
          txt == "ぶさいくね" or
          txt == "ブサイクね" or
          txt == "ぶす" or
          txt == "ブス" or
          txt == "不細工" or
          txt == "ぶさいく" or
          txt == "ブサイク" or
          txt == "最低ですね" or
          txt == "さいていですね" or
          txt == "サイテーですね" or
          txt == "最低だね" or
          txt == "さいていだね" or
          txt == "サイテーだね" or
          txt == "最低だな" or
          txt == "さいていだな" or
          txt == "サイテーだな" or
          txt == "最低だわ" or
          txt == "さいていだわ" or
          txt == "サイテーだわ" or
          txt == "最低よ" or
          txt == "さいていよ" or
          txt == "サイテーよ" or
          txt == "最低ね" or
          txt == "さいていね" or
          txt == "サイテーね" or
          txt == "最低" or
          txt == "さいてい" or
          txt == "サイテー" or
          txt == "この無能野郎め" or
          txt == "この無能やろうめ" or
          txt == "この無能ヤロウめ" or
          txt == "この無能ヤローめ" or
          txt == "この無能め" or
          txt == "この無能野郎が" or
          txt == "この無能やろうが" or
          txt == "この無能ヤロウが" or
          txt == "この無能ヤローが" or
          txt == "無能野郎め" or
          txt == "無能やろうめ" or
          txt == "無能ヤロウめ" or
          txt == "無能ヤローめ" or
          txt == "無能め" or
          txt == "無能野郎が" or
          txt == "無能やろうが" or
          txt == "無能ヤロウが" or
          txt == "無能ヤローが" or
          txt == "無能ですね" or
          txt == "無能だね" or
          txt == "無能だわ" or
          txt == "無能よ" or
          txt == "無能ね" or
          txt == "無能" or
          txt == "この馬鹿野郎め" or
          txt == "このばか野郎め" or
          txt == "このバカ野郎め" or
          txt == "この馬鹿やろうめ" or
          txt == "このばかやろうめ" or
          txt == "このバカやろうめ" or
          txt == "この馬鹿ヤロウめ" or
          txt == "この馬鹿ヤローめ" or
          txt == "この馬鹿野郎が" or
          txt == "このばか野郎が" or
          txt == "このバカ野郎が" or
          txt == "この馬鹿やろうが" or
          txt == "このばかやろうが" or
          txt == "このバカやろうが" or
          txt == "この馬鹿ヤロウが" or
          txt == "この馬鹿ヤロが" or
          txt == "このばかヤロウが" or
          txt == "このばかヤローが" or
          txt == "この馬鹿野郎" or
          txt == "このばか野郎" or
          txt == "このバカ野郎" or
          txt == "この馬鹿やろう" or
          txt == "このばかやろう" or
          txt == "このバカやろう" or
          txt == "この馬鹿ヤロウ" or
          txt == "この馬鹿ヤロー" or
          txt == "このばかヤロウ" or
          txt == "このばかヤロー" or
          txt == "このバカヤロウ" or
          txt == "このバカヤロー" or
          txt == "馬鹿野郎ですね" or
          txt == "ばか野郎ですね" or
          txt == "バカ野郎ですね" or
          txt == "馬鹿やろうですね" or
          txt == "ばかやろうですね" or
          txt == "バカやろうですね" or
          txt == "馬鹿ヤロウですね" or
          txt == "馬鹿ヤローですね" or
          txt == "ばかヤロウですね" or
          txt == "ばかヤロですね" or
          txt == "バカヤロウですね" or
          txt == "バカヤローですね" or
          txt == "馬鹿野郎" or
          txt == "ばか野郎" or
          txt == "バカ野郎" or
          txt == "馬鹿やろう" or
          txt == "ばかやろう" or
          txt == "バカやろう" or
          txt == "馬鹿ヤロウ" or
          txt == "ばかヤロウ" or
          txt == "バカヤロウ" or
          txt == "バカヤロー" or
          txt == "馬鹿だわ" or
          txt == "ばかだわ" or
          txt == "バカだわ" or
          txt == "馬鹿ね" or
          txt == "ばかね" or
          txt == "バカね" or
          txt == "馬鹿め" or
          txt == "ばかめ" or
          txt == "バカめ" or
          txt == "馬鹿が" or
          txt == "ばかが" or
          txt == "バカが" or
          txt == "馬鹿" or
          txt == "ばか" or
          txt == "バカ" or
          txt == "あほですね" or
          txt == "アホですね" or
          txt == "あほだね" or
          txt == "アホだね" or
          txt == "あほだわ" or
          txt == "アホだわ" or
          txt == "あほね" or
          txt == "アホね" or
          txt == "あほ" or
          txt == "アホ" or
          txt == "このあほ垂れ" or
          txt == "このアホ垂れ" or
          txt == "あほ垂れ" or
          txt == "アホ垂れ" or
          txt == "このあほたれ" or
          txt == "このアホたれ" or
          txt == "あほたれ" or
          txt == "アホたれ" or
          txt == "このあほタレ" or
          txt == "このアホタレ" or
          txt == "あほタレ" or
          txt == "アホタレ" or
          txt == "このくず野郎め" or
          txt == "このくずやろうめ" or
          txt == "このくずヤロウめ" or
          txt == "このくずヤローめ" or
          txt == "このクズ野郎め" or
          txt == "このクズやろうめ" or
          txt == "このクズヤロウめ" or
          txt == "このクズヤローめ" or
          txt == "このくず野郎が" or
          txt == "このくずやろうが" or
          txt == "このくずヤロウが" or
          txt == "このくずヤローが" or
          txt == "このクズ野郎が" or
          txt == "このクズやろうが" or
          txt == "このクズヤロウが" or
          txt == "このクズヤローが" or
          txt == "くず野郎め" or
          txt == "くずやろうめ" or
          txt == "くずヤロウめ" or
          txt == "くずヤローめ" or
          txt == "クズ野郎め" or
          txt == "クズやろうめ" or
          txt == "クズヤロウめ" or
          txt == "クズヤローめ" or
          txt == "くず野郎が" or
          txt == "くずやろうが" or
          txt == "くずヤロウが" or
          txt == "くずヤロが" or
          txt == "クズ野郎が" or
          txt == "クズやろうが" or
          txt == "クズヤロウが" or
          txt == "クズヤローが" or
          txt == "このくず" or
          txt == "このクズ" or
          txt == "くず" or
          txt == "クズ" or
          txt == "このかす野郎め" or
          txt == "このかすやろうめ" or
          txt == "このかすヤロウめ" or
          txt == "このかすヤローめ" or
          txt == "このカス野郎め" or
          txt == "このカスやろうめ" or
          txt == "このカスヤロウめ" or
          txt == "このカスヤローめ" or
          txt == "このかす野郎が" or
          txt == "このかすやろうが" or
          txt == "このかすヤロウが" or
          txt == "このかすヤローが" or
          txt == "このカス野郎が" or
          txt == "このカスやろうが" or
          txt == "このカスヤロウが" or
          txt == "このカスヤローが" or
          txt == "かす野郎め" or
          txt == "かすやろうめ" or
          txt == "かすヤロウめ" or
          txt == "かすヤローめ" or
          txt == "カス野郎め" or
          txt == "カスやろうめ" or
          txt == "カスヤロウめ" or
          txt == "カスヤローめ" or
          txt == "かす野郎が" or
          txt == "かすやろうが" or
          txt == "かすヤロウが" or
          txt == "かすヤローが" or
          txt == "カス野郎が" or
          txt == "カスやろうが" or
          txt == "カスヤロウが" or
          txt == "カスヤローが" or
          txt == "このかす" or
          txt == "このカス" or
          txt == "かす" or
          txt == "カス" or
          txt == "このごみ野郎め" or
          txt == "このごみやろうめ" or
          txt == "このごみヤロウめ" or
          txt == "このごみヤローめ" or
          txt == "このゴミ野郎め" or
          txt == "このゴミやろうめ" or
          txt == "このゴミヤロウめ" or
          txt == "このゴミヤローめ" or
          txt == "このかす野郎が" or
          txt == "このかすやろうが" or
          txt == "このかすヤロウが" or
          txt == "このかすヤローが" or
          txt == "このゴミ野郎が" or
          txt == "このゴミやろうが" or
          txt == "このゴミヤロウが" or
          txt == "このゴミヤローが" or
          txt == "ごみ野郎め" or
          txt == "ごみやろうめ" or
          txt == "ごみヤロウめ" or
          txt == "ごみヤローめ" or
          txt == "ゴミ野郎め" or
          txt == "ゴミやろうめ" or
          txt == "ゴミヤロウめ" or
          txt == "ゴミヤローめ" or
          txt == "かす野郎が" or
          txt == "かすやろうが" or
          txt == "かすヤロウが" or
          txt == "かすヤローが" or
          txt == "ゴミ野郎が" or
          txt == "ゴミやろうが" or
          txt == "ゴミヤロウが" or
          txt == "ゴミヤローが" or
          txt == "このごみ" or
          txt == "このゴミ" or
          txt == "ごみ" or
          txt == "ゴミ" or
          txt == "このげす野郎め" or
          txt == "このげすやろうめ" or
          txt == "このげすヤロウめ" or
          txt == "このげすヤローめ" or
          txt == "このゲス野郎め" or
          txt == "このゲスやろうめ" or
          txt == "このゲスヤロウめ" or
          txt == "このゲスヤローめ" or
          txt == "このげす野郎が" or
          txt == "このげすやろうが" or
          txt == "このげすヤロウが" or
          txt == "このげすヤローが" or
          txt == "このゲス野郎が" or
          txt == "このゲスやろうが" or
          txt == "このゲスヤロウが" or
          txt == "このゲスヤローが" or
          txt == "このげす" or
          txt == "このゲス" or
          txt == "げす" or
          txt == "ゲス"):
           extrctd_intnt = "罵倒＆貶め"
    elif (txt == "邪魔" or
          txt == "じゃま" or
          txt == "ジャマ" or
          txt == "目障り" or
          txt == "うざったい" or
          txt == "ウザったい" or
          txt == "ウザい" or
          txt == "消えてください" or
          txt == "消えて" or
          txt == "消えな" or
          txt == "消え失せろ" or
          txt == "消えうせろ" or
          txt == "消えろ" or
          txt == "死んでください" or
          txt == "氏んでください" or
          txt == "しんでください" or
          txt == "死んで" or
          txt == "氏んで" or
          txt == "しんで" or
          txt == "死ね" or
          txt == "氏ね" or
          txt == "しね" or
          txt == "死になさい" or
          txt == "氏になさい" or
          txt == "しになさい" or
          txt == "死にな" or
          txt == "氏にな" or
          txt == "しにな" or
          txt == "死んでろ" or
          txt == "氏んでろ" or
          txt == "しんでろ"):
           extrctd_intnt = "人格・存在否定:罵声に近い"
    elif (txt == "大天才ですか" or
          txt == "天才ですか" or
          txt == "大秀才ですか" or
          txt == "秀才ですか" or
          txt == "優秀ですか"):
           extrctd_intnt = "称賛＆礼賛:半疑問"
    elif (txt == "無能ですか" or
          txt == "ばかですか" or
          txt == "バカですか" or
          txt == "あほですか" or
          txt == "アホですか" or
          txt == "くずですか" or
          txt == "クズですか" or
          txt == "かすですか" or
          txt == "カスですか" or
          txt == "ごみですか" or
          txt == "ゴミですか"):
           extrctd_intnt = "罵詈＆罵倒:半疑問"
    elif (txt == "何をしていますか" or
          txt == "なにをしていますか" or
          txt == "何をしてますか" or
          txt == "なにをしてますか" or
          txt == "何してますか" or
          txt == "なにしてますか" or
          txt == "何してるの" or
          txt == "なにしてるの" or
          txt == "どうしていますか" or
          txt == "どうしてますか" or
          txt == "どうしてる"):
           extrctd_intnt = "疑義＆質問＆確認:現在形,状態や状況について"
    elif (txt == "何をしてきましたか" or
          txt == "なにをしてきましたか" or
          txt == "何をしてましたか" or
          txt == "なにをしてましたか" or
          txt == "何してましたか" or
          txt == "なにしてましたか" or
          txt == "何してたの" or
          txt == "なにしてたの" or
          txt == "何してた" or
          txt == "なにしてた" or
          txt == "どうしてきましたか" or
          txt == "どうしてましたか" or
          txt == "どうしてた"):
           extrctd_intnt = "疑義＆質問＆確認:過去形,状態や状況について"
    elif (txt == "何をしたいですか" or
          txt == "なにをしたいですか" or
          txt == "何がしたいですか" or
          txt == "なにがしたいですか" or
          txt == "何したいですか" or
          txt == "なにしたいですか" or
          txt == "何したいの" or
          txt == "なにしたいの" or
          txt == "何したい" or
          txt == "なにしたい" or
          txt == "何をしますか" or
          txt == "なにをしますか" or
          txt == "何しますか" or
          txt == "なにしますか" or
          txt == "なにします"):
           extrctd_intnt = "疑義＆質問＆確認:現在形,願望や欲求について"
    elif (txt == "何をしたかったのですか" or
          txt == "なにをしたかったのですか" or
          txt == "何をしたかったんですか" or
          txt == "なにをしたかったんですか" or
          txt == "何がしたかったのですか" or
          txt == "なにがしたかったのですか" or
          txt == "何がしたかったんですか" or
          txt == "なにがしたかったんですか" or
          txt == "何したかったのですか" or
          txt == "なにしたかったのですか" or
          txt == "何したかったんですか" or
          txt == "なにしたかったんですか" or
          txt == "何したかったの" or
          txt == "なにしたかったの"):
           extrctd_intnt = "疑義＆質問＆確認:過去形,願望や欲求について"
    elif (txt == "何をしていきたいのですか" or
          txt == "なにをしていきたいのですか" or
          txt == "何をしていきたいですか" or
          txt == "なにをしていきたいですか" or
          txt == "何をしていきたいの" or
          txt == "なにをしていきたいの" or
          txt == "何がしていきたいのですか" or
          txt == "なにがしていきたいのですか" or
          txt == "何がしていきたいですか" or
          txt == "なにがしていきたいですか" or
          txt == "何していきたいのですか" or
          txt == "なにしていきたいのですか" or
          txt == "何していきたいんですか" or
          txt == "なにしていきたいんですか" or
          txt == "何していきたいですか" or
          txt == "なにしていきたいですか" or
          txt == "何していきたいの" or
          txt == "なにしていきたいの" or
          txt == "何していきたい" or
          txt == "なにしていきたい"):
           extrctd_intnt = "疑義＆質問＆確認:未来形,願望や欲求について"
    elif (txt == "どうしたいのですか" or
          txt == "どうしたいんですか" or
          txt == "どうしたいですか" or
          txt == "どうしたいのかな" or
          txt == "どうしたいの" or
          txt == "どうしたい"):
           extrctd_intnt = "疑義＆質問＆確認:現在形,願望や欲求について,漠然とした様子や様相"
    elif (txt == "どうしたかったのですか" or
          txt == "どうしたかったんですか" or
          txt == "どうしたかったの" or
          txt == "どうしたかった"):
           extrctd_intnt = "疑義＆質問＆確認:過去形,願望や欲求について,漠然とした様子や様相"
    elif (txt == "どうしていきたいのですか" or
          txt == "どうしていきたいんですか" or
          txt == "どうしていきたいの" or
          txt == "どうしていきたい"):
           extrctd_intnt = "疑義＆質問＆確認:未来形,願望や欲求について,漠然とした様子や様相"
    elif (txt == "どうなのですか" or
          txt == "どうなんですか" or
          txt == "どうなの" or
          txt == "どうなん"):
           extrctd_intnt = "疑義＆質問＆確認:意図や目的について"
    elif txt == "どう":
           extrctd_intnt = "疑義＆質問＆確認:感想や感慨について"
    elif (txt == "どうしてなのですか" or
          txt == "どうしてなんですか" or
          txt == "どうしてですか" or
          txt == "どうして"):
           extrctd_intnt = "疑義＆質問＆確認:理由や事情について"      
    elif (txt == "何故なのですか" or
          txt == "なぜなのですか" or
          txt == "何故なんですか" or
          txt == "なぜなんですか" or
          txt == "何故ですか" or
          txt == "なぜですか" or
          txt == "何故" or
          txt == "なぜ" or
          txt == "何で" or
          txt == "なんで"):
           extrctd_intnt = "疑義＆質問＆確認:理由や事情について"
    elif (txt == "良いです" or
          txt == "よいです" or
          txt == "いいです" or
          txt == "良い" or
          txt == "いい" or
          txt == "おっけー" or
          txt == "オッケー" or
          txt == "おけ" or
          txt == "オケ" or
          txt == "OK"):
           extrctd_intnt = "許容＆許可"
    elif (txt == "駄目です" or
          txt == "だめです" or
          txt == "ダメです" or
          txt == "駄目だ" or
          txt == "だめだ" or
          txt == "ダメだ" or
          txt == "駄目" or
          txt == "だめ" or
          txt == "ダメ" or
          txt == "禁止です" or
          txt == "禁止だ" or
          txt == "禁止" or
          txt == "いけません" or
          txt == "いけない" or
          txt == "しては駄目です" or
          txt == "してはだめです" or
          txt == "してはダメです" or
          txt == "しては駄目だ" or
          txt == "してはだめだ" or
          txt == "してはダメだ" or
          txt == "しては駄目" or
          txt == "してはだめ" or
          txt == "してはダメ" or
          txt == "するのは禁止です" or
          txt == "するのは禁止" or
          txt == "やるのは禁止です" or
          txt == "やるのは禁止" or
          txt == "してははいけません" or
          txt == "しちゃいけません" or
          txt == "やってはいけません" or
          txt == "やっちゃいけません" or
          txt == "やっちゃ駄目" or
          txt == "やっちゃだめ" or
          txt == "やっちゃダメ" or
          txt == "NG"):
           extrctd_intnt = "禁止＆不許可"
    elif (txt == "ですねえ" or
          txt == "ですねぇ" or
          txt == "ですね" or
          txt == "そうだねえ" or
          txt == "そうだねぇ" or
          txt == "そうだね" or
          txt == "そだねえ" or
          txt == "そだねぇ" or
          txt == "そだね" or
          txt == "だよねえ" or
          txt == "だよねぇ" or
          txt == "だよね" or
          txt == "だねえ" or
          txt == "だねぇ" or
          txt == "だね"):
           extrctd_intnt = "賛意＆賛同"
    elif (txt == "許可を頂きたいです" or
          txt == "許可をいただきたいです" or
          txt == "許可を頂きたい" or
          txt == "許可をいただきたい" or
          txt == "許可を下さい" or
          txt == "許可をください" or
          txt == "許可して下さい" or
          txt == "許可してください" or
          txt == "許可してくれ" or
          txt == "許可して"):
           extrctd_intnt = "依頼＆要求:許可を求めている"
    elif (txt == "歌ってよ" or
          txt == "うたってよ" or
          txt == "歌って" or
          txt == "うたって" or
          txt == "踊ってよ" or
          txt == "おどってよ" or
          txt == "踊って" or
          txt == "おどって" or
          txt == "遊んでよ" or
          txt == "あそんでよ" or
          txt == "遊んで" or
          txt == "あそんで"):
           extrctd_intnt = "依頼＆要求:遊び心を求めている"
    elif (txt == "行きます" or
          txt == "いきます" or
          txt == "遣ります" or
          txt == "やります" or
          txt == "遊びます" or
          txt == "あそびます" or
          txt == "休みます" or
          txt == "やすみます"):
           extrctd_intnt = "宣言＆表明:現在進行形,未来形"
    elif (txt == "美しい" or
          txt == "うつくしい" or
          txt == "楽しい" or
          txt == "たのしい" or
          txt == "苦しい" or
          txt == "くるしい" or
          txt == "辛い" or
          txt == "つらい" or
          txt == "嬉しい" or
          txt == "うれしい" or
          txt == "悲しい" or
          txt == "かなしい" or
          txt == "哀しい"):
           extrctd_intnt = "表出＆表現:心理や感情の状態"
    elif (txt == "楽" or
          txt == "らく" or
          txt == "ラク" or
          txt == "らくちん" or
          txt == "ラクチン" or
          txt == "楽勝" or
          txt == "らくしょう" or
          txt == "ラクショウ" or
          txt == "大変" or
          txt == "たいへん" or
          txt == "タイヘン" or
          txt == "疲れた" or
          txt == "つかれた"):
           extrctd_intnt = "表出＆表現:精神や肉体の状態"
    elif (txt == "最初は グー" or
          txt == "最初はグー" or
          txt == "じゃんけんぽん" or
          txt == "じゃんけん" or
          txt == "ジャンケンポン" or
          txt == "ジャンケン"):
           extrctd_intnt = "児戯＆遊戯"
    elif (txt == "お願い致します" or
          txt == "お願いいたします" or
          txt == "お願いします" or
          txt == "お願いです" or
          txt == "お願い"):
           extrctd_intnt = "依頼＆依願"
    elif (txt == "申し訳ございません" or
          txt == "申し訳ありません" or
          txt == "御免なさい" or
          txt == "ごめんなさい" or
          txt == "ゴメンなさい" or
          txt == "御免" or
          txt == "ごめん" or
          txt == "ゴメン" or
          txt == "メンゴ メンゴ" or
          txt == "メンゴメンゴ" or
          txt == "メンゴ" or
          txt == "すみません" or
          txt == "すいません" or
          txt == "すまん"):
           extrctd_intnt = "感謝＆お礼"
    elif (txt == "申し訳ございません" or
          txt == "申し訳ありません" or
          txt == "御免なさい" or
          txt == "ごめんなさい" or
          txt == "ゴメンなさい" or
          txt == "御免" or
          txt == "ごめん" or
          txt == "ゴメン" or
          txt == "メンゴ メンゴ" or
          txt == "メンゴメンゴ" or
          txt == "メンゴ" or
          txt == "すみません" or
          txt == "すいません" or
          txt == "すまん"):
           extrctd_intnt = "陳謝＆謝罪"
    elif (txt == "承知致しました" or
          txt == "承知いたしました" or
          txt == "承知しました" or
          txt == "承知した" or
          txt == "承知" or
          txt == "かしこまりました" or
          txt == "かしこまり"):
           extrctd_intnt = "承知＆承諾"
    elif (txt == "了解致しました" or
          txt == "了解いたしました" or
          txt == "了解しました" or
          txt == "了解した" or
          txt == "了解" or
          txt == "りょ" or
          txt == "リョ" or
          txt == "分かりました" or
          txt == "わかりました" or
          txt == "分かった" or
          txt == "わかった"):
           extrctd_intnt = "了承＆了解"
    elif (txt == "愛しています" or
          txt == "あいしています" or
          txt == "愛してます" or
          txt == "あいしてます" or
          txt == "愛してる" or
          txt == "あいしてる" or
          txt == "好きです" or
          txt == "すきです" or
          txt == "スキです" or
          txt == "好きだ" or
          txt == "すきだ" or
          txt == "スキだ" or
          txt == "好き" or
          txt == "すき" or
          txt == "スキ"):
           extrctd_intnt = "求愛＆熱情"
    elif (txt == "Hなことしたい" or
          txt == "Hなことしよう" or
          txt == "Hしたい" or
          txt == "Hしよう" or
          txt == "セックスしたい" or
          txt == "セックスしよう"):
           extrctd_intnt = "発情＆欲情"
    elif (txt == "セックスは好きですか" or
          txt == "セックスは好き" or
          txt == "どこを責められたい" or
          txt == "どこ責められたい"):
           extrctd_intnt = "辱め:卑猥な言動"
    elif (txt == "何故そうなるのですか" or
          txt == "なぜそうなるのですか" or
          txt == "何故そうなるんですか" or
          txt == "なぜそうなるんですか" or
          txt == "何故そうなるのか" or
          txt == "なぜそうなるのか" or
          txt == "何故そうなるか" or
          txt == "なぜそうなるか" or
          txt == "何故そうなるのです" or
          txt == "なぜそうなるのです" or
          txt == "何故そうなるんです" or
          txt == "なぜそうなるんです"):
           extrctd_intnt = "疑義＆確認＆質問:目上や年上の者に対して,理由や事情について"
    elif (txt == "なんでそうなるのかなあ" or
          txt == "なんでそうなるのかなぁ" or
          txt == "なんでそうなるのかな" or
          txt == "なんでそうなるかなあ" or
          txt == "なんでそうなるかなぁ" or
          txt == "なんでそうなるかな" or
          txt == "なんでそうなるのか" or
          txt == "なんでそうなるか" or
          txt == "なんでそうなる" or
          txt == "何故そうなるの" or
          txt == "なぜそうなるの" or
          txt == "何故そうなる" or
          txt == "なぜそうなる"):
           extrctd_intnt = "疑義＆確認＆質問:やや反発,やや反感,目下の者に対して,理由や事情について"
    elif (txt == "大丈夫でしょうか" or
          txt == "大丈夫ですか" or
          txt == "大丈夫"):
           extrctd_intnt = "疑義＆質問＆確認:安否や健康状態について"
    elif (txt == "ご苦労様でした" or
          txt == "ご苦労様です" or
          txt == "ご苦労様" or
          txt == "ご苦労" or
          txt == "お疲れ様でした" or
          txt == "お疲れ様です" or
          txt == "お疲れ様" or
          txt == "お疲れ" or
          txt == "大儀であった" or
          txt == "大儀だった"):        
           extrctd_intnt = "慰労＆労い"
    elif (txt == "分かった" or
          txt == "わかった"):
           extrctd_intnt = "理解＆認識"
    elif (txt == "恐悦至極にございます" or
          txt == "恐悦至極でございます" or
          txt == "恐悦至極です" or
          txt == "恐れ入ります" or
          txt == "恐れ多いです" or
          txt == "とんでもございません" or
          txt == "とんでもない"):
           extrctd_intnt = "訴求＆表現:褒められ,感謝され,恐縮している"
    elif (txt == "きざったらしい" or
          txt == "キザったらしい" or
          txt == "きざっぽい" or
          txt == "キザっぽい" or
          txt == "嫌味ったらしい" or
          txt == "イヤミったらしい" or
          txt == "嫌味っぽい" or
          txt == "イヤミっぽい"):
           extrctd_intnt = "訴求＆表現:反発して,反感を抱いて,強い嫌悪"
    elif (txt == "しても良いですか" or
          txt == "してもよいですか" or
          txt == "良いですか" or
          txt == "いいですか" or
          txt == "良いか" or
          txt == "いいか" or
          txt == "してもいいですか" or
          txt == "してもいいか" or
          txt == "していいか" or
          txt == "いいか" or
          txt == "やっても良いですか" or
          txt == "やってもよいですか" or
          txt == "やってもいいですか" or
          txt == "やってもいいか" or
          txt == "やっていいか"):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,許容や許可を求める"
    elif (txt == "駄目ですか" or
          txt == "だめですか" or
          txt == "ダメですか" or
          txt == "駄目か" or
          txt == "だめか" or
          txt == "ダメか" or
          txt == "禁止ですか" or
          txt == "禁止か" or
          txt == "いけませんか" or
          txt == "いけないか"):
           extrctd_intnt = "疑義＆質問＆確認:否定形,許容や許可を求める"
    elif (txt == "お伺いします" or
          txt == "お聞きします"):
           extrctd_intnt = "聴取＆傾聴:用件を尋ねる"
    elif (txt == "お聞かせ下さい" or
          txt == "お聞かせください"):
           extrctd_intnt = "聴取＆傾聴:意見や感想を求める"
    elif (txt == "お考えになって下さい" or
          txt == "お考え下さい" or
          txt == "考えて下さい" or
          txt == "考えてください" or
          txt == "考えてくれ" or
          txt == "考えて"):
           extrctd_intnt = "要求＆要請:思慮や思考を求める"
    elif (txt == "考え直して下さい" or
          txt == "考え直してください" or
          txt == "考え直してくれ" or
          txt == "考え直して" or
          txt == "思い直して下さい" or
          txt == "思い直してください" or
          txt == "思い直してくれ" or
          txt == "思い直して"):
           extrctd_intnt = "要求＆要請:再度の思慮や思考を求める"
    elif (txt == "良きに計らえ" or
          txt == "よきに計らえ" or
          txt == "良しなに" or
          txt == "よしなに" or
          txt == "どうぞ良しなに" or
          txt == "どうぞよしなに"):
           extrctd_intnt = "要求＆要請:善処を求める"
    elif (txt == "うむ" or
          txt == "ウム" or
          txt == "うん" or
          txt == "ウン"):
           extrctd_intnt = "了承＆承諾:納得する様子でもある"
    elif (txt == "そう言っているのです" or
          txt == "そういっているのです" or
          txt == "そう言っているんです" or
          txt == "そういっているんです" or
          txt == "そう言っている" or
          txt == "そういっている" or
          txt == "そう言ってる" or
          txt == "そういってる"):
           extrctd_intnt = "問答:肯定形,考えや意見に同意する形・恰好で"
    elif (txt == "そうは言っていないよ" or
          txt == "そうはいっていないよ" or
          txt == "そうは言っていない" or
          txt == "そうはいっていない" or
          txt == "そうは言ってないよ" or
          txt == "そうはいってないよ" or
          txt == "そうは言ってない" or
          txt == "そうはいってない"):
           extrctd_intnt = "問答:否定形,考えや意見に反意する形・恰好で"
    elif (txt == "しますよね" or
          txt == "するよね" or
          txt == "やるよね"):
           extrctd_intnt = "疑義＆質問＆確認:肯定形"
    elif (txt == "しませんよね" or
          txt == "しないよね" or
          txt == "やらないよね"):
           extrctd_intnt = "疑義＆質問＆確認:否定形"
    elif (txt == "するよな" or
          txt == "やるよな"):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,半強制"
    elif (txt == "しないよな" or
          txt == "せんよな" or
          txt == "やらないよな" or
          txt == "やらんよな"):
           extrctd_intnt = "疑義＆質問＆確認:否定形,半強制"
    elif (txt == "そうなのですね" or
          txt == "そうなんですね" or
          txt == "そうなのだな" or
          txt == "そうなんだな"):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,気持ちや考えを察する形・恰好で"
    elif (txt == "そうではないのですね" or
          txt == "そうではないんですね" or
          txt == "そうではないのだな" or
          txt == "そうではないんだな"):
           extrctd_intnt = "疑義＆質問＆確認:否定形,気持ちや考えを察する形・恰好で"
    elif (txt == "そうみたいだよ" or
          txt == "そうみたいだね" or
          txt == "そうみたいだな" or
          txt == "そうみたいだわ" or
          txt == "そうみたいだ" or
          txt == "そうみたい" or
          txt == "そうらしいよ" or
          txt == "そうらしいね" or
          txt == "そうらしいな" or
          txt == "そうらしいわ" or
          txt == "そうらしい"):
           extrctd_intnt = "同意:意見や考えに沿う形・恰好で"
    elif (txt == "そうではないらしいよ" or
          txt == "そうではないらしいね" or
          txt == "そうではないらしいな" or
          txt == "そうではないらしいわ" or
          txt == "そうではないらしい" or
          txt == "ではないらしいよ" or
          txt == "ではないらしいね" or
          txt == "ではないらしいな" or
          txt == "ではないらしいわ" or
          txt == "ではないらしい" or
          txt == "そうじゃないらしいよ" or
          txt == "そうじゃないらしいね" or
          txt == "そうじゃないらしいな" or
          txt == "そうじゃないらしいわ" or
          txt == "そうじゃないらしい"):
           extrctd_intnt = "反意＆不同意:意見や考えに沿わない形・恰好で"
    elif (txt == "そうなのですね" or
          txt == "そうなんですね" or
          txt == "そうなんですね" or
          txt == "なのですね" or
          txt == "なんですね"):
           extrctd_intnt = "理解＆納得:肯定形"
    elif (txt == "そうではないのですね" or
          txt == "そうではないんですね" or
          txt == "そうじゃないんですね" or
          txt == "ではないのですね" or
          txt == "ではないんですね" or
          txt == "じゃないんですね"):
           extrctd_intnt = "理解＆納得:否定形"
    elif (txt == "お分かりいただけましたか" or
          txt == "分かっていただけましたか" or
          txt == "分かりましたか" or
          txt == "分かっていますか" or
          txt == "分かってますか"):
           extrctd_intnt = "疑義＆質問＆確認:認識力や理解力を試すことに近い"
    elif (txt == "いかがなさいますか" or
          txt == "いかがいたしましょうか" or
          txt == "どういたしますか" or
          txt == "どうしますか" or
          txt == "どうするのですか" or
          txt == "どうするんですか" or
          txt == "どうするの" or
          txt == "どうするん" or
          txt == "どうする"):
           extrctd_intnt = "疑義＆質問＆確認:丁寧かつ敬って,今後の動きや活動について"
    elif (txt == "ではどうするのですか" or
          txt == "ではどうするんですか" or
          txt == "ではどうするのか" or
          txt == "ではどうするの" or
          txt == "ではどうする" or
          txt == "じゃあどうするのか" or
          txt == "じゃあどうするの" or
          txt == "じゃあどうする"):
           extrctd_intnt = "疑義＆質問＆確認:責任追求に近い,今後の動きや活動について"
    elif (txt == "いらっしゃいませ" or
          txt == "いらっしゃい" or
          txt == "どうぞ ごゆっくりなさって下さい" or
          txt == "どうぞ ごゆっくりなさってください" or
          txt == "どうぞごゆっくりなさってください" or
          txt == "どうぞ ごゆっくりなさって" or
          txt == "どうぞごゆっくりなさって" or
          txt == "ごゆっくりなさって下さい" or
          txt == "ごゆっくりなさってください" or
          txt == "ごゆっくりなさって" or
          txt == "ごゆっくり どうぞ" or
          txt == "ごゆっくりどうぞ" or
          txt == "ごゆっくり"):
           extrctd_intnt = "歓迎＆歓待:くつろいで欲しいという気持ち"
    elif (txt == "どうぞ お手柔らかに" or
          txt == "どうぞお手柔らかに"):
           extrctd_intnt = "常套句＆決まり文句:配慮や手加減などを求めて"
    elif (txt == "どうぞ 宜しくお願い致します" or
          txt == "どうぞ よろしくお願い致します" or
          txt == "どうぞ よろしくお願いいたします" or
          txt == "どうぞ お願いいたします" or
          txt == "どうぞ よろしくお願いします" or
          txt == "どうぞ よろしく" or
          txt == "どうぞ宜しくお願い致します" or
          txt == "どうぞよろしくお願い致します" or
          txt == "どうぞよろしくお願いいたします" or
          txt == "どうぞお願いいたします" or
          txt == "どうぞよろしくお願いします" or
          txt == "どうぞよろしく" or
          txt == "よろしく どうぞ" or
          txt == "よろしくどうぞ" or
          txt == "よろしく"):
           extrctd_intnt = "常套句＆決まり文句:友好・良好な関係を求めて"
    elif (txt == "頑張りましょう" or
          txt == "がんばりましょう" or
          txt == "ぼちぼち やりましょう" or
          txt == "ぼちぼちやりましょう" or
          txt == "ボチボチ やりましょう" or
          txt == "ボチボチやりましょう" or
          txt == "ゆっくり 行きましょう" or
          txt == "ゆっくり いきましょう" or
          txt == "ゆっくり行きましょう" or
          txt == "ゆっくりいきましょう" or
          txt == "ゆっくりしましょう" or
          txt == "急いで行きましょう" or
          txt == "急いでいきましょう" or
          txt == "急いでやりましょう" or
          txt == "急ぎましょう" or
          txt == "優しく行きましょう" or
          txt == "優しくしましょう" or
          txt == "厳しく行きましょう" or
          txt == "厳しくしましょう"):
           extrctd_intnt = "推奨＆強制＆勧告:誘導に近い"
    elif (txt == "本当ですよ" or
          txt == "ホントですよ" or
          txt == "本当だよ" or
          txt == "ホントだよ" or
          txt == "本当よ" or
          txt == "ホントよ" or
          txt == "ホント ホント" or
          txt == "ホントホント"):
           extrctd_intnt = "告知＆宣告:真実であることを告げる"
    elif (txt == "嘘ですよ" or
          txt == "ウソですよ" or
          txt == "嘘だよ" or
          txt == "ウソですよ" or
          txt == "嘘よ" or
          txt == "ウソよ" or
          txt == "ウソ ウソ" or
          txt == "ウソウソ"):
           extrctd_intnt = "告知＆宣告:虚偽であることを告げる"
    elif (txt == "本当ですか" or
          txt == "ホントですか" or
          txt == "本当か" or
          txt == "ホントか" or
          txt == "ホント"):
           extrctd_intnt = "疑義＆質問＆確認:真実であるかどうか"
    elif (txt == "嘘ですか" or
          txt == "ウソですか" or
          txt == "嘘か" or
          txt == "ウソか" or
          txt == "嘘" or
          txt == "ウソ"):
           extrctd_intnt = "疑義＆質問＆確認:虚偽であるかどうか"
    elif (txt == "左様ですか" or
          txt == "そうですか" or
          txt == "はい はい" or
          txt == "はいはい" or
          txt == "うん うん" or
          txt == "うんうん"):
           extrctd_intnt = "相槌＆合いの手:傾聴している素振り"
    elif (txt == "その通りです" or
          txt == "その通り"):
           extrctd_intnt = "相槌＆合いの手:正鵠を得た相手に対して"
    elif (txt == "賛成" or
          txt == "反対"):
           extrctd_intnt = "単純な返答:投票,二者択一式"
    elif (txt == "はい" or
          txt == "いいえ"):
           extrctd_intnt = "単純な返答:一般,二者択一式"
    else:
           extrctd_intnt = "不明・その他"


    return extrctd_intnt


#テキストからインテント(＝発話の意図＆種類＆類型)を抽出する
def extract_intent_from_general_text(txt):
    extrctd_intnt_txt = txt

    if (check_text_terminate_string(txt, "を行います") or
        check_text_terminate_string(txt, "を行う") or
        check_text_terminate_string(txt, "をします") or
        check_text_terminate_string(txt, "をする") or
        check_text_terminate_string(txt, "はします") or
        check_text_terminate_string(txt, "はする") or
        check_text_terminate_string(txt, "します") or
        check_text_terminate_string(txt, "する")):
         extrctd_intnt = "宣言＆表明:現在形,未来形,能動形,肯定形"
    elif (check_text_terminate_string(txt, "を行いません") or
          check_text_terminate_string(txt, "を行わない") or
          check_text_terminate_string(txt, "をしません") or
          check_text_terminate_string(txt, "をしない") or
          check_text_terminate_string(txt, "はしません") or
          check_text_terminate_string(txt, "はしない") or
          check_text_terminate_string(txt, "しません") or
          check_text_terminate_string(txt, "しない")):
           extrctd_intnt = "宣言＆表明:現在形,未来形,能動形,否定形"
    elif (check_text_terminate_string(txt, "を行っています") or
          check_text_terminate_string(txt, "を行っている") or
          check_text_terminate_string(txt, "をしています") or
          check_text_terminate_string(txt, "をしてます") or
          check_text_terminate_string(txt, "をしている") or
          check_text_terminate_string(txt, "をしてる") or
          check_text_terminate_string(txt, "しています") or
          check_text_terminate_string(txt, "してます") or
          check_text_terminate_string(txt, "している") or
          check_text_terminate_string(txt, "してる")):
           extrctd_intnt = "宣言＆表明:現在進行形,能動形,肯定形"
    elif (check_text_terminate_string(txt, "を行っていません") or
          check_text_terminate_string(txt, "を行ってません") or
          check_text_terminate_string(txt, "をしていません") or
          check_text_terminate_string(txt, "をしてません") or
          check_text_terminate_string(txt, "をしていない") or
          check_text_terminate_string(txt, "をしてない") or
          check_text_terminate_string(txt, "していません") or
          check_text_terminate_string(txt, "してません") or
          check_text_terminate_string(txt, "していない") or
          check_text_terminate_string(txt, "してない")):
           extrctd_intnt = "宣言＆表明:現在進行形,能動形,否定形"
    elif (check_text_terminate_string(txt, "ができています") or
          check_text_terminate_string(txt, "ができている") or
          check_text_terminate_string(txt, "ができてる") or
          check_text_terminate_string(txt, "できています") or
          check_text_terminate_string(txt, "できている") or
          check_text_terminate_string(txt, "できてる")):
          extrctd_intnt = "宣言＆表明:現在進行形,完了形(＝已然形),肯定形"
    elif (check_text_terminate_string(txt, "ができていません") or
          check_text_terminate_string(txt, "ができてません") or
          check_text_terminate_string(txt, "ができていない") or
          check_text_terminate_string(txt, "ができてない") or
          check_text_terminate_string(txt, "できていません") or
          check_text_terminate_string(txt, "できてません") or
          check_text_terminate_string(txt, "できていない") or
          check_text_terminate_string(txt, "できてない")):
           extrctd_intnt = "宣言＆表明:現在進行形,未完了形(＝未然形),否定形"
    elif (check_text_terminate_string(txt, "ができます") or
          check_text_terminate_string(txt, "ができる") or
          check_text_terminate_string(txt, "できます") or
          check_text_terminate_string(txt, "できる")):
           extrctd_intnt = "宣言＆表明:可能形,肯定形"
    elif (check_text_terminate_string(txt, "ができません") or
          check_text_terminate_string(txt, "ができない") or
          check_text_terminate_string(txt, "できません") or
          check_text_terminate_string(txt, "できない")):
           extrctd_intnt = "宣言＆表明:不可能形,否定形"
    elif (check_text_terminate_string(txt, "をしました") or
          check_text_terminate_string(txt, "をした") or
          check_text_terminate_string(txt, "はしました") or
          check_text_terminate_string(txt, "はした") or
          check_text_terminate_string(txt, "しました") or
          check_text_terminate_string(txt, "した") or
          check_text_terminate_string(txt, "をやりました") or
          check_text_terminate_string(txt, "をやった") or
          check_text_terminate_string(txt, "はやりました") or
          check_text_terminate_string(txt, "はやった")):
           extrctd_intnt = "宣言＆表明:過去,能動形,肯定形"
    elif (check_text_terminate_string(txt, "をしていません") or
          check_text_terminate_string(txt, "をしてません") or
          check_text_terminate_string(txt, "をしてない") or
          check_text_terminate_string(txt, "はしていません") or
          check_text_terminate_string(txt, "はしてません") or
          check_text_terminate_string(txt, "はしてない") or
          check_text_terminate_string(txt, "していません") or
          check_text_terminate_string(txt, "してません") or
          check_text_terminate_string(txt, "してない") or
          check_text_terminate_string(txt, "をやってません") or
          check_text_terminate_string(txt, "をやってない") or
          check_text_terminate_string(txt, "はやってません") or
          check_text_terminate_string(txt, "はやってない")):
           extrctd_intnt = "宣言＆表明:過去形,能動形,否定形"
    elif (check_text_terminate_string(txt, "をするのですか") or
          check_text_terminate_string(txt, "をするんですか") or
          check_text_terminate_string(txt, "をしますか") or
          check_text_terminate_string(txt, "はするのですか") or
          check_text_terminate_string(txt, "はするんですか") or
          check_text_terminate_string(txt, "はしますか") or
          check_text_terminate_string(txt, "するのですか") or
          check_text_terminate_string(txt, "するんですか") or
          check_text_terminate_string(txt, "しますか") or
          check_text_terminate_string(txt, "するのか") or
          check_text_terminate_string(txt, "するか")):
           extrctd_intnt = "疑義＆質問＆確認:現在形,未来形,能動形,肯定形"
    elif (check_text_terminate_string(txt, "をしないのですか") or
          check_text_terminate_string(txt, "はしないのですか") or
          check_text_terminate_string(txt, "をしないんですか") or
          check_text_terminate_string(txt, "はしないんですか") or
          check_text_terminate_string(txt, "をしないのか") or
          check_text_terminate_string(txt, "はしないのか") or
          check_text_terminate_string(txt, "しないのですか") or
          check_text_terminate_string(txt, "しないんですか") or
          check_text_terminate_string(txt, "しないのか")):
           extrctd_intnt = "疑義＆質問＆確認:現在形,未来形,能動形,否定形"
    elif (check_text_terminate_string(txt, "をしていますか") or
          check_text_terminate_string(txt, "はしていますか") or
          check_text_terminate_string(txt, "をしてますか") or
          check_text_terminate_string(txt, "はしてますか") or
          check_text_terminate_string(txt, "をしているか") or
          check_text_terminate_string(txt, "はしているか") or
          check_text_terminate_string(txt, "をしてるか") or
          check_text_terminate_string(txt, "はしてるか") or
          check_text_terminate_string(txt, "していますか") or
          check_text_terminate_string(txt, "してますか") or
          check_text_terminate_string(txt, "しているか") or
          check_text_terminate_string(txt, "してるか")):
           extrctd_intnt = "疑義＆質問＆確認:現在進行形,能動形,肯定形"
    elif (check_text_terminate_string(txt, "をしていませんか") or
          check_text_terminate_string(txt, "はしていませんか") or
          check_text_terminate_string(txt, "をしてませんか") or
          check_text_terminate_string(txt, "はしてませんか") or
          check_text_terminate_string(txt, "をしていないか") or
          check_text_terminate_string(txt, "はしていないか") or
          check_text_terminate_string(txt, "をしてないか") or
          check_text_terminate_string(txt, "はしてないか") or
          check_text_terminate_string(txt, "していませんか") or
          check_text_terminate_string(txt, "してませんか") or
          check_text_terminate_string(txt, "していないか") or
          check_text_terminate_string(txt, "してないか")):
           extrctd_intnt = "疑義＆質問＆確認:現在進行形,能動形,否定形"
    elif (check_text_terminate_string(txt, "ができていますか") or
          check_text_terminate_string(txt, "はできていますか") or
          check_text_terminate_string(txt, "ができてますか") or
          check_text_terminate_string(txt, "はできてますか") or
          check_text_terminate_string(txt, "ができているか") or
          check_text_terminate_string(txt, "はできているか") or
          check_text_terminate_string(txt, "ができてるか") or
          check_text_terminate_string(txt, "はできてるか") or
          check_text_terminate_string(txt, "できていますか") or
          check_text_terminate_string(txt, "できてますか") or
          check_text_terminate_string(txt, "できているか") or
          check_text_terminate_string(txt, "できてるか")):
           extrctd_intnt = "疑義＆質問＆確認:現在,完了形(＝已然形),肯定形,物事の進行や進捗について"
    elif (check_text_terminate_string(txt, "はできていませんか") or
          check_text_terminate_string(txt, "はできてませんか") or
          check_text_terminate_string(txt, "はできていないか") or
          check_text_terminate_string(txt, "はできてないか") or
          check_text_terminate_string(txt, "できていませんか") or
          check_text_terminate_string(txt, "できてませんか") or
          check_text_terminate_string(txt, "できていないか") or
          check_text_terminate_string(txt, "できてないか")):
           extrctd_intnt = "疑義＆質問＆確認:現在,未完了形(＝已然形),否定形,物事の進行や進捗について"
    elif (check_text_terminate_string(txt, "ができましたか") or
          check_text_terminate_string(txt, "はできましたか") or
          check_text_terminate_string(txt, "ができたか") or
          check_text_terminate_string(txt, "はできたか") or
          check_text_terminate_string(txt, "できましたか") or
          check_text_terminate_string(txt, "できたか")):
           extrctd_intnt = "疑義＆質問＆確認:過去,完了形(＝已然形),肯定形,物事の進行や進捗について"
    elif (check_text_terminate_string(txt, "はできていませんか") or
          check_text_terminate_string(txt, "はできてませんか") or
          check_text_terminate_string(txt, "はできてないか") or
          check_text_terminate_string(txt, "できていませんか") or
          check_text_terminate_string(txt, "できてませんか") or
          check_text_terminate_string(txt, "できてないか")):
           extrctd_intnt = "疑義＆質問＆確認:過去,未完了形(＝已然形),否定形,物事の進行や進捗について"
    elif (check_text_terminate_string(txt, "ができますか") or
          check_text_terminate_string(txt, "はできますか") or
          check_text_terminate_string(txt, "ができるか") or
          check_text_terminate_string(txt, "はできるか") or
          check_text_terminate_string(txt, "できますか") or
          check_text_terminate_string(txt, "できるか")):
           extrctd_intnt = "疑義＆質問＆確認:現在＆未来,肯定形,物事の可能性について"
    elif (check_text_terminate_string(txt, "はできませんか") or
          check_text_terminate_string(txt, "はできないか") or
          check_text_terminate_string(txt, "できませんか") or
          check_text_terminate_string(txt, "できないか")):
           extrctd_intnt = "疑義＆質問＆確認:現在＆未来,否定形,物事の可能性について"
    elif (check_text_terminate_string(txt, "がされています") or
          check_text_terminate_string(txt, "はされています") or
          check_text_terminate_string(txt, "がされてます") or
          check_text_terminate_string(txt, "はされてます") or
          check_text_terminate_string(txt, "がされている") or
          check_text_terminate_string(txt, "はされている") or
          check_text_terminate_string(txt, "がされてる") or
          check_text_terminate_string(txt, "はされてる") or
          check_text_terminate_string(txt, "されています") or
          check_text_terminate_string(txt, "されてます") or
          check_text_terminate_string(txt, "されている") or
          check_text_terminate_string(txt, "がやられています") or
          check_text_terminate_string(txt, "がやられてます") or
          check_text_terminate_string(txt, "がやられてる") or
          check_text_terminate_string(txt, "はやられています") or
          check_text_terminate_string(txt, "はやられてます") or
          check_text_terminate_string(txt, "はやられてる")):
           extrctd_intnt = "宣言＆表明:現在進行形,受動形,肯定形"
    elif (check_text_terminate_string(txt, "がされていません") or
          check_text_terminate_string(txt, "はされていません") or
          check_text_terminate_string(txt, "されていません") or
          check_text_terminate_string(txt, "がされてません") or
          check_text_terminate_string(txt, "はされてません") or
          check_text_terminate_string(txt, "されてません") or
          check_text_terminate_string(txt, "がされていない") or
          check_text_terminate_string(txt, "はされていない") or
          check_text_terminate_string(txt, "されていない") or
          check_text_terminate_string(txt, "がされてない") or
          check_text_terminate_string(txt, "はされてない") or
          check_text_terminate_string(txt, "されてない")):
           extrctd_intnt = "宣言＆表明:現在進行形,受動形,否定形"
    elif (check_text_terminate_string(txt, "がされました") or
          check_text_terminate_string(txt, "はされました") or
          check_text_terminate_string(txt, "されました") or
          check_text_terminate_string(txt, "がされた") or
          check_text_terminate_string(txt, "はされた") or
          check_text_terminate_string(txt, "された")):
           extrctd_intnt = "宣言＆表明:過去完了形(＝已然形),受動形,肯定形"
    elif (check_text_terminate_string(txt, "がされませんでした") or
          check_text_terminate_string(txt, "はされませんでした") or
          check_text_terminate_string(txt, "されませんでした") or
          check_text_terminate_string(txt, "がされなかった") or
          check_text_terminate_string(txt, "はされなかった") or
          check_text_terminate_string(txt, "されなかった")):
           extrctd_intnt = "宣言＆表明:過去完了形(＝已然形),受動形,否定形"
    elif (check_text_terminate_string(txt, "でした") or
          check_text_terminate_string(txt, "だった")):
           extrctd_intnt = "宣言＆表明:過去完了形(＝已然形),肯定形"
    elif (check_text_terminate_string(txt, "ではなかったです") or
          check_text_terminate_string(txt, "でなかったです") or
          check_text_terminate_string(txt, "ではなかった") or
          check_text_terminate_string(txt, "でなかった")):
           extrctd_intnt = "宣言＆表明:過去完了形(＝已然形),否定形"
    elif (check_text_terminate_string(txt, "をしていきたい") or
          check_text_terminate_string(txt, "はしていきたい") or
          check_text_terminate_string(txt, "していきたい") or
          check_text_terminate_string(txt, "をやっていきたい") or
          check_text_terminate_string(txt, "はやっていきたい")):
           extrctd_intnt = "宣言＆表明:現在＆未来,持続 能動形,肯定形"
    elif (check_text_terminate_string(txt, "をしていきたくはない") or
          check_text_terminate_string(txt, "はしていきたくはない") or
          check_text_terminate_string(txt, "していきたくはない") or
          check_text_terminate_string(txt, "をしていきたくない") or
          check_text_terminate_string(txt, "はしていきたくない") or
          check_text_terminate_string(txt, "していきたくない") or
          check_text_terminate_string(txt, "をやっていきたくはない") or
          check_text_terminate_string(txt, "はやっていきたくはない") or
          check_text_terminate_string(txt, "をやっていきたくない") or
          check_text_terminate_string(txt, "はやっていきたくない")):
           extrctd_intnt = "宣言＆表明:現在＆未来,持続 能動形,否定形"
    elif (check_text_terminate_string(txt, "ではありました") or
          check_text_terminate_string(txt, "ではあった") or
          check_text_terminate_string(txt, "であった")):
           extrctd_intnt = "宣言＆表明:過去＆現在,肯定形,事実や現実について"
    elif (check_text_terminate_string(txt, "ではありませんでした") or
          check_text_terminate_string(txt, "ではなかった") or
          check_text_terminate_string(txt, "でなかった")):
           extrctd_intnt = "宣言＆表明:現在＆未来,否定形,事実や現実について"
    elif (check_text_terminate_string(txt, "で御座います") or
          check_text_terminate_string(txt, "でございます") or
          check_text_terminate_string(txt, "であります") or
          check_text_terminate_string(txt, "です")):
           extrctd_intnt = "紹介＆説明＆提示:肯定形"
    elif (check_text_terminate_string(txt, "では御座いません") or
          check_text_terminate_string(txt, "ではございません") or
          check_text_terminate_string(txt, "ではありません")):
           extrctd_intnt = "紹介＆説明＆提示:否定形"
    elif (check_text_terminate_string(txt, "をやっていました") or
          check_text_terminate_string(txt, "をやってました") or
          check_text_terminate_string(txt, "をやってた")):
           extrctd_intnt = "報告＆連絡 過去＆現在:能動形,肯定形"
    elif (check_text_terminate_string(txt, "をやっていませんでした") or
          check_text_terminate_string(txt, "をやってませんでした") or
          check_text_terminate_string(txt, "をやってなかった")):
           extrctd_intnt = "報告＆連絡 過去＆現在:能動形,否定形"
    elif (check_text_terminate_string(txt, "を致しませんか") or
          check_text_terminate_string(txt, "をいたしませんか") or
          check_text_terminate_string(txt, "致しませんか") or
          check_text_terminate_string(txt, "いたしませんか") or
          check_text_terminate_string(txt, "しませんか")):
           extrctd_intnt = "誘導＆勧誘"
    elif (check_text_terminate_string(txt, "を行いたい") or
          check_text_terminate_string(txt, "をしたい") or
          check_text_terminate_string(txt, "がしたい") or
          check_text_terminate_string(txt, "したい") or
          check_text_terminate_string(txt, "をやりたい") or
          check_text_terminate_string(txt, "がやりたい")):
           extrctd_intnt = "願望＆欲求:肯定形"
    elif (check_text_terminate_string(txt, "を行いたくない") or
          check_text_terminate_string(txt, "をしたくない") or
          check_text_terminate_string(txt, "がしたくない") or
          check_text_terminate_string(txt, "したくない") or
          check_text_terminate_string(txt, "をやりたくない") or
          check_text_terminate_string(txt, "がやりたくない")):
           extrctd_intnt = "願望＆欲求:否定形"
    elif (check_text_terminate_string(txt, "を行いたいのですか") or
          check_text_terminate_string(txt, "を行いたいんですか") or
          check_text_terminate_string(txt, "を行いたいですか") or
          check_text_terminate_string(txt, "をしたいのですか") or
          check_text_terminate_string(txt, "をしたいんですか") or
          check_text_terminate_string(txt, "をしたいですか") or
          check_text_terminate_string(txt, "は行いたいのですか") or
          check_text_terminate_string(txt, "は行いたいんですか") or
          check_text_terminate_string(txt, "は行いたいですか") or
          check_text_terminate_string(txt, "はしたいのですか") or
          check_text_terminate_string(txt, "はしたいんですか") or
          check_text_terminate_string(txt, "はしたいですか") or
          check_text_terminate_string(txt, "したいのですか") or
          check_text_terminate_string(txt, "したいんですか") or
          check_text_terminate_string(txt, "したいですか") or
          check_text_terminate_string(txt, "したいのか") or
          check_text_terminate_string(txt, "したいか") or
          check_text_terminate_string(txt, "をやりたいのですか") or
          check_text_terminate_string(txt, "をやりたいんですか") or
          check_text_terminate_string(txt, "をやりたいですか") or
          check_text_terminate_string(txt, "をやりたいのか") or
          check_text_terminate_string(txt, "をやりたいか") or
          check_text_terminate_string(txt, "がやりたいのですか") or
          check_text_terminate_string(txt, "がやりたいんですか") or
          check_text_terminate_string(txt, "がやりたいですか") or
          check_text_terminate_string(txt, "がやりたいのか") or
          check_text_terminate_string(txt, "がやりたいか")):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,他者の願望や欲求に適う、他者の行為や行動について"
    elif (check_text_terminate_string(txt, "を行いたくないのですか") or
          check_text_terminate_string(txt, "を行いたくないんですか") or
          check_text_terminate_string(txt, "を行いたくないですか") or
          check_text_terminate_string(txt, "をしたくないのですか") or
          check_text_terminate_string(txt, "をしたくないんですか") or
          check_text_terminate_string(txt, "をしたくないですか") or
          check_text_terminate_string(txt, "は行いたくないのですか") or
          check_text_terminate_string(txt, "は行いたくないんですか") or
          check_text_terminate_string(txt, "は行いたくないですか") or
          check_text_terminate_string(txt, "はしたくないのですか") or
          check_text_terminate_string(txt, "はしたくないんですか") or
          check_text_terminate_string(txt, "はしたくないですか") or
          check_text_terminate_string(txt, "したくないのですか") or
          check_text_terminate_string(txt, "したくないんですか") or
          check_text_terminate_string(txt, "したくないですか") or
          check_text_terminate_string(txt, "したくないか") or
          check_text_terminate_string(txt, "をやりたくないのですか") or
          check_text_terminate_string(txt, "をやりたくないんですか") or
          check_text_terminate_string(txt, "をやりたくないですか") or
          check_text_terminate_string(txt, "をやりたくないか") or
          check_text_terminate_string(txt, "がやりたくないのですか") or
          check_text_terminate_string(txt, "がやりたくないんですか") or
          check_text_terminate_string(txt, "がやりたくないですか") or
          check_text_terminate_string(txt, "がやりたくないのか") or
          check_text_terminate_string(txt, "がやりたくないか")):
           extrctd_intnt = "疑義＆質問＆確認:否定形,他者の願望や欲求に適う、他者の行為や行動について"
    elif (check_text_terminate_string(txt, "をしていきたいですか") or
          check_text_terminate_string(txt, "をしていきたいか") or
          check_text_terminate_string(txt, "していきたいか") or
          check_text_terminate_string(txt, "をやっていきたいですか") or
          check_text_terminate_string(txt, "をやっていきたいか")):
           extrctd_intnt = "疑義＆質問＆確認:現在＆未来,肯定形,他者の願望や欲求に適う、他者の行為や行動について"
    elif (check_text_terminate_string(txt, "をしていきたくないですか") or
          check_text_terminate_string(txt, "はしていきたくないですか") or
          check_text_terminate_string(txt, "していきたくないですか") or
          check_text_terminate_string(txt, "をしていきたくないか") or
          check_text_terminate_string(txt, "はしていきたくないか") or
          check_text_terminate_string(txt, "していきたくないか") or
          check_text_terminate_string(txt, "はやっていきたくないか") or
          check_text_terminate_string(txt, "をやっていきたくないか")):
           extrctd_intnt = "疑義＆質問＆確認:現在＆未来,否定形,他者の願望や欲求に適う、他者の行為や行動について"
    elif (check_text_terminate_string(txt, "をやり続けたいですか") or
          check_text_terminate_string(txt, "をやり続けたいか") or
          check_text_terminate_string(txt, "をやってたいですか") or
          check_text_terminate_string(txt, "をやってたいか") or
          check_text_terminate_string(txt, "をし続けたいですか") or
          check_text_terminate_string(txt, "をし続けたいか") or
          check_text_terminate_string(txt, "をしてたいですか") or
          check_text_terminate_string(txt, "をしてたいか")):
           extrctd_intnt = "疑義＆質問＆確認:現在＆未来,肯定形,持続的 他者の願望や欲求に適う、他者の行為や行動について"
    elif (check_text_terminate_string(txt, "をやり続けたくないですか") or
          check_text_terminate_string(txt, "をやり続けたくないか") or
          check_text_terminate_string(txt, "をやってたくないですか") or
          check_text_terminate_string(txt, "をやってたくないか") or
          check_text_terminate_string(txt, "をし続けたくないですか") or
          check_text_terminate_string(txt, "をし続けたくないか") or
          check_text_terminate_string(txt, "をしてたくないですか") or
          check_text_terminate_string(txt, "をしてたくないか")):
           extrctd_intnt = "疑義＆質問＆確認:現在＆未来,肯定形,持続的 他者の願望や欲求に適う、他者の行為や行動について"
    elif (check_text_terminate_string(txt, "をしましたか") or
          check_text_terminate_string(txt, "をしたか") or
          check_text_terminate_string(txt, "はしましたか") or
          check_text_terminate_string(txt, "はしたか") or
          check_text_terminate_string(txt, "しましたか") or
          check_text_terminate_string(txt, "したか") or
          check_text_terminate_string(txt, "をやりましたか") or
          check_text_terminate_string(txt, "をやったか") or
          check_text_terminate_string(txt, "はやりましたか") or
          check_text_terminate_string(txt, "はやったか")):
           extrctd_intnt = "疑義＆質問＆確認:過去,能動形,肯定形,他者の行為や行動について"
    elif (check_text_terminate_string(txt, "をしていませんか") or
          check_text_terminate_string(txt, "をしてませんか") or
          check_text_terminate_string(txt, "をしてないか") or
          check_text_terminate_string(txt, "はしていませんか") or
          check_text_terminate_string(txt, "はしてませんか") or
          check_text_terminate_string(txt, "はしてないか") or
          check_text_terminate_string(txt, "していませんか") or
          check_text_terminate_string(txt, "してませんか") or
          check_text_terminate_string(txt, "してないか")):
           extrctd_intnt = "疑義＆質問＆確認:過去,能動形,否定形,他者の行為や行動について"
    elif (check_text_terminate_string(txt, "はされていますか") or
          check_text_terminate_string(txt, "されていますか") or
          check_text_terminate_string(txt, "されてますか") or
          check_text_terminate_string(txt, "されてますか")):
           extrctd_intnt = "疑義＆質問＆確認:現在,受動形,肯定形,他者の行為や行動について,物事の進行や進捗について"
    elif (check_text_terminate_string(txt, "はされていませんか") or
          check_text_terminate_string(txt, "されていませんか") or
          check_text_terminate_string(txt, "されてませんか") or
          check_text_terminate_string(txt, "されていないか") or
          check_text_terminate_string(txt, "されてないか")):
           extrctd_intnt = "疑義＆質問＆確認:現在,受動形,否定形,他者の行為や行動について,物事の進行や進捗について"
    elif (check_text_terminate_string(txt, "はされていましたか") or
          check_text_terminate_string(txt, "はされてましたか") or
          check_text_terminate_string(txt, "されてましたか") or
          check_text_terminate_string(txt, "されてたか")):
           extrctd_intnt = "疑義＆質問＆確認:現在,受動形,肯定形,他者の行為や行動について,物事の進行や進捗について"
    elif (check_text_terminate_string(txt, "はされていませんでしたか") or
          check_text_terminate_string(txt, "はされていなかったか") or
          check_text_terminate_string(txt, "されていませんでしたか") or
          check_text_terminate_string(txt, "されていなかったか")):
           extrctd_intnt = "疑義＆質問＆確認:現在,受動形,否定形,他者の行為や行動について,物事の進行や進捗について"
    elif (check_text_terminate_string(txt, "だったですか") or
          check_text_terminate_string(txt, "だったか") or
          check_text_terminate_string(txt, "でしたか")):
           extrctd_intnt = "疑義＆質問＆確認:過去完了形(＝已然形),肯定形,他者の状況や状態について,物事の進行や進捗について"
    elif (check_text_terminate_string(txt, "ではなかったですか") or
          check_text_terminate_string(txt, "ではなかったか") or
          check_text_terminate_string(txt, "でなかったか")):
           extrctd_intnt = "疑義＆質問＆確認:過去完了形(＝已然形),否定形,他者の状況や状態について,物事の進行や進捗について"
    elif (check_text_terminate_string(txt, "をしなさい") or
          check_text_terminate_string(txt, "をしろ") or
          check_text_terminate_string(txt, "はしなさい") or
          check_text_terminate_string(txt, "はしろ") or
          check_text_terminate_string(txt, "しなさい") or
          check_text_terminate_string(txt, "しろ")):
           extrctd_intnt = "指示＆命令"
    elif (check_text_terminate_string(txt, "をしなければならない") or
          check_text_terminate_string(txt, "をしなければ") or
          check_text_terminate_string(txt, "をしないといけないです") or
          check_text_terminate_string(txt, "をしないといけない") or
          check_text_terminate_string(txt, "をしなきゃいけないです") or
          check_text_terminate_string(txt, "をしなきゃいけない") or
          check_text_terminate_string(txt, "をしなきゃならない") or
          check_text_terminate_string(txt, "をしなきゃ") or
          check_text_terminate_string(txt, "はしなければならない") or
          check_text_terminate_string(txt, "はしなければ") or
          check_text_terminate_string(txt, "はしないといけないです") or
          check_text_terminate_string(txt, "はしないといけない") or
          check_text_terminate_string(txt, "はしなきゃいけないです") or
          check_text_terminate_string(txt, "はしなきゃいけない") or
          check_text_terminate_string(txt, "はしなきゃならない") or
          check_text_terminate_string(txt, "はしなきゃ") or
          check_text_terminate_string(txt, "しなければならない") or
          check_text_terminate_string(txt, "しなければ") or
          check_text_terminate_string(txt, "しないといけないです") or
          check_text_terminate_string(txt, "しないといけない") or
          check_text_terminate_string(txt, "しなきゃいけないです") or
          check_text_terminate_string(txt, "しなきゃいけない") or
          check_text_terminate_string(txt, "しなきゃならない") or
          check_text_terminate_string(txt, "しなきゃ")):
           extrctd_intnt = "強制＆勧告:肯定形"
    elif (check_text_terminate_string(txt, "がしなければならない") or
          check_text_terminate_string(txt, "がしなければ") or
          check_text_terminate_string(txt, "がしないといけないです") or
          check_text_terminate_string(txt, "がしないといけない") or
          check_text_terminate_string(txt, "がしなきゃいけないです") or
          check_text_terminate_string(txt, "がしなきゃいけない") or
          check_text_terminate_string(txt, "がしなきゃならない") or
          check_text_terminate_string(txt, "がしなきゃ")):
           extrctd_intnt = "強制＆勧告:肯定形,特定個人についてのみ"
    elif (check_text_terminate_string(txt, "はしてはならない") or
          check_text_terminate_string(txt, "はしてはいけない") or
          check_text_terminate_string(txt, "はしたらいけない") or
          check_text_terminate_string(txt, "はしちゃいけない") or
          check_text_terminate_string(txt, "をしてはならない") or
          check_text_terminate_string(txt, "をしてはいけない") or
          check_text_terminate_string(txt, "をしたらいけない") or
          check_text_terminate_string(txt, "をしちゃいけない") or
          check_text_terminate_string(txt, "してはならない") or
          check_text_terminate_string(txt, "してはいけない") or
          check_text_terminate_string(txt, "したらいけない") or
          check_text_terminate_string(txt, "しちゃいけない")):
           extrctd_intnt = "強制＆勧告:否定形"
    elif (check_text_terminate_string(txt, "がしてはならない") or
          check_text_terminate_string(txt, "がしてはいけない") or
          check_text_terminate_string(txt, "がしたらいけない") or
          check_text_terminate_string(txt, "がしちゃいけない")):
           extrctd_intnt = "強制＆勧告:否定形,特定個人についてのみ"
    elif (check_text_terminate_string(txt, "はしなければならないのですか") or
          check_text_terminate_string(txt, "はしなければならないんですか") or
          check_text_terminate_string(txt, "はしなければならないですか") or
          check_text_terminate_string(txt, "はしなければいけないですか") or
          check_text_terminate_string(txt, "はしないといけないですか") or
          check_text_terminate_string(txt, "はしなきゃいけないですか") or
          check_text_terminate_string(txt, "はしなきゃいけないか") or
          check_text_terminate_string(txt, "はしなきゃならないか") or
          check_text_terminate_string(txt, "をしなければならないのですか") or
          check_text_terminate_string(txt, "をしなければならないんですか") or
          check_text_terminate_string(txt, "をしなければならないですか") or
          check_text_terminate_string(txt, "をしなければいけないですか") or
          check_text_terminate_string(txt, "をしないといけないですか") or
          check_text_terminate_string(txt, "をしなきゃいけないですか") or
          check_text_terminate_string(txt, "をしなきゃいけないか") or
          check_text_terminate_string(txt, "をしなきゃならないか") or
          check_text_terminate_string(txt, "しなければならないのですか") or
          check_text_terminate_string(txt, "しなければならないんですか") or
          check_text_terminate_string(txt, "しなければならないですか") or
          check_text_terminate_string(txt, "しなければいけないですか") or
          check_text_terminate_string(txt, "しないといけないですか") or
          check_text_terminate_string(txt, "しなきゃいけないですか") or
          check_text_terminate_string(txt, "しなきゃいけないか") or
          check_text_terminate_string(txt, "しなきゃならないか")):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,強制や勧告について"
    elif (check_text_terminate_string(txt, "がしなければならないのですか") or
          check_text_terminate_string(txt, "がしなければならないんですか") or
          check_text_terminate_string(txt, "がしなければならないのか") or
          check_text_terminate_string(txt, "がしなければならないか") or
          check_text_terminate_string(txt, "がしないといけないですか") or
          check_text_terminate_string(txt, "がしないといけないか") or
          check_text_terminate_string(txt, "がしなきゃいけないですか") or
          check_text_terminate_string(txt, "がしなきゃいけないのか") or
          check_text_terminate_string(txt, "がしなきゃいけないか")):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,強制や勧告について,特定個人についてのみ"
    elif (check_text_terminate_string(txt, "はしてはならないのか") or
          check_text_terminate_string(txt, "はしてはならないか") or
          check_text_terminate_string(txt, "はしてはいけないか") or
          check_text_terminate_string(txt, "はしたらいけないか") or
          check_text_terminate_string(txt, "はしちゃいけないか") or
          check_text_terminate_string(txt, "をしてはならないのか") or
          check_text_terminate_string(txt, "をしてはならないか") or
          check_text_terminate_string(txt, "をしてはいけないか") or
          check_text_terminate_string(txt, "をしたらいけないか") or
          check_text_terminate_string(txt, "をしちゃいけないか") or
          check_text_terminate_string(txt, "してはならないのか") or
          check_text_terminate_string(txt, "してはならないか") or
          check_text_terminate_string(txt, "してはいけないか") or
          check_text_terminate_string(txt, "したらいけないか") or
          check_text_terminate_string(txt, "しちゃいけないか")):
           extrctd_intnt = "疑義＆質問＆確認:否定形,強制や勧告について"
    elif (check_text_terminate_string(txt, "がしてはならないのか") or
          check_text_terminate_string(txt, "がしてはならないか") or
          check_text_terminate_string(txt, "がしてはいけないか") or
          check_text_terminate_string(txt, "がしたらいけないか") or
          check_text_terminate_string(txt, "がしちゃいけないか")):
           extrctd_intnt = "疑義＆質問＆確認:否定形,強制や勧告について,特定個人についてのみ"
    elif (check_text_terminate_string(txt, "はするべきです") or
          check_text_terminate_string(txt, "をするべきです") or
          check_text_terminate_string(txt, "はすべきです") or
          check_text_terminate_string(txt, "をすべきです") or
          check_text_terminate_string(txt, "するべきです") or
          check_text_terminate_string(txt, "すべきです")):
           extrctd_intnt = "宣言＆表明:肯定形,行為や行動の是非について"
    elif (check_text_terminate_string(txt, "はするべきではないです") or
          check_text_terminate_string(txt, "をするべきではないです") or
          check_text_terminate_string(txt, "はすべきではないです") or
          check_text_terminate_string(txt, "をすべきではないです") or
          check_text_terminate_string(txt, "はすべきではないです") or
          check_text_terminate_string(txt, "をすべきではないです") or
          check_text_terminate_string(txt, "するべきではないです") or
          check_text_terminate_string(txt, "するべきでない") or
          check_text_terminate_string(txt, "すべきでない")):
           extrctd_intnt = "宣言＆表明:否定形,行為や行動の是非について"
    elif (check_text_terminate_string(txt, "をするべきでしょうか") or
          check_text_terminate_string(txt, "はするべきでしょうか") or
          check_text_terminate_string(txt, "をすべきでしょうか") or
          check_text_terminate_string(txt, "はすべきでしょうか") or
          check_text_terminate_string(txt, "するべきでしょうか") or
          check_text_terminate_string(txt, "すべきでしょうか")):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,行為や行動の是非について"
    elif (check_text_terminate_string(txt, "をするべきではないのでしょうか") or
          check_text_terminate_string(txt, "はするべきではないのでしょうか") or
          check_text_terminate_string(txt, "をすべきではないのでしょうか") or
          check_text_terminate_string(txt, "はすべきではないのでしょうか") or
          check_text_terminate_string(txt, "するべきではないのでしょうか") or
          check_text_terminate_string(txt, "すべきではないのでしょうか") or
          check_text_terminate_string(txt, "すべきでないのでしょうか")):
           extrctd_intnt = "疑義＆質問＆確認:否定形,行為や行動の是非について"
    elif (check_text_terminate_string(txt, "をしても良いです") or
          check_text_terminate_string(txt, "をしてもいいです") or
          check_text_terminate_string(txt, "をして良いです") or
          check_text_terminate_string(txt, "をしていいです") or
          check_text_terminate_string(txt, "をしても良い") or
          check_text_terminate_string(txt, "をしてもいい") or
          check_text_terminate_string(txt, "をして良い") or
          check_text_terminate_string(txt, "をしていい") or
          check_text_terminate_string(txt, "はしても良いです") or
          check_text_terminate_string(txt, "はしてもいいです") or
          check_text_terminate_string(txt, "はして良いです") or
          check_text_terminate_string(txt, "はしていいです") or
          check_text_terminate_string(txt, "はしても良い") or
          check_text_terminate_string(txt, "はしてもいい") or
          check_text_terminate_string(txt, "はして良い") or
          check_text_terminate_string(txt, "はしていい") or
          check_text_terminate_string(txt, "をやっても良いです") or
          check_text_terminate_string(txt, "をやってもいいです") or
          check_text_terminate_string(txt, "はやっても良いです") or
          check_text_terminate_string(txt, "はやってもいいです") or
          check_text_terminate_string(txt, "しても良いです") or
          check_text_terminate_string(txt, "してもいいです") or
          check_text_terminate_string(txt, "して良いです") or
          check_text_terminate_string(txt, "していいです") or
          check_text_terminate_string(txt, "しても良い") or
          check_text_terminate_string(txt, "してもいい") or
          check_text_terminate_string(txt, "して良い") or
          check_text_terminate_string(txt, "していい")):
           extrctd_intnt = "許容＆許可"
    elif (check_text_terminate_string(txt, "をしないように") or
          check_text_terminate_string(txt, "をしないよう") or
          check_text_terminate_string(txt, "をするな") or
          check_text_terminate_string(txt, "をしてはいけない") or
          check_text_terminate_string(txt, "をしちゃいけない") or
          check_text_terminate_string(txt, "はしないように") or
          check_text_terminate_string(txt, "はしないよう") or
          check_text_terminate_string(txt, "はするな") or
          check_text_terminate_string(txt, "はしてはいけない") or
          check_text_terminate_string(txt, "はしちゃいけない") or
          check_text_terminate_string(txt, "をやってはいけない") or
          check_text_terminate_string(txt, "をやっちゃいけない") or
          check_text_terminate_string(txt, "はやってはいけない") or
          check_text_terminate_string(txt, "はやっちゃいけない") or
          check_text_terminate_string(txt, "をしちゃ駄目だ") or
          check_text_terminate_string(txt, "をしちゃだめだ") or
          check_text_terminate_string(txt, "をしちゃダメだ") or
          check_text_terminate_string(txt, "はしちゃ駄目だ") or
          check_text_terminate_string(txt, "はしちゃだめだ") or
          check_text_terminate_string(txt, "をしちゃ駄目") or
          check_text_terminate_string(txt, "をしちゃだめ") or
          check_text_terminate_string(txt, "をしちゃダメ") or
          check_text_terminate_string(txt, "はしちゃ駄目") or
          check_text_terminate_string(txt, "はしちゃだめ") or
          check_text_terminate_string(txt, "しないように") or
          check_text_terminate_string(txt, "しないよう") or
          check_text_terminate_string(txt, "するな") or
          check_text_terminate_string(txt, "してはいけない") or
          check_text_terminate_string(txt, "しちゃいけない") or
          check_text_terminate_string(txt, "はいけない") or
          check_text_terminate_string(txt, "しちゃ駄目だ") or
          check_text_terminate_string(txt, "しちゃだめだ") or
          check_text_terminate_string(txt, "しちゃダメだ") or
          check_text_terminate_string(txt, "しちゃ駄目") or
          check_text_terminate_string(txt, "しちゃだめ") or
          check_text_terminate_string(txt, "しちゃダメ")):
           extrctd_intnt = "禁止＆制限"
    elif (check_text_terminate_string(txt, "がしないように") or
          check_text_terminate_string(txt, "がしないよう") or
          check_text_terminate_string(txt, "がするな") or
          check_text_terminate_string(txt, "がやってはいけない") or
          check_text_terminate_string(txt, "がやっちゃいけない") or
          check_text_terminate_string(txt, "がやっちゃ駄目だ") or
          check_text_terminate_string(txt, "がやっちゃだめだ") or
          check_text_terminate_string(txt, "がやっちゃダメだ") or
          check_text_terminate_string(txt, "がやっちゃ駄目") or
          check_text_terminate_string(txt, "がやっちゃだめ") or
          check_text_terminate_string(txt, "がやっちゃダメ") or
          check_text_terminate_string(txt, "がしちゃ駄目だ") or
          check_text_terminate_string(txt, "がしちゃだめだ") or
          check_text_terminate_string(txt, "がしちゃダメだ") or
          check_text_terminate_string(txt, "がしちゃ駄目") or
          check_text_terminate_string(txt, "がしちゃだめ") or
          check_text_terminate_string(txt, "がしちゃダメ")):
           extrctd_intnt = "禁止＆制限:特定の個人についてのみ"
    elif (check_text_terminate_string(txt, "をしてはいけませんか") or
          check_text_terminate_string(txt, "をしてはいけないですか") or
          check_text_terminate_string(txt, "をしてはいけないか") or
          check_text_terminate_string(txt, "はしてはいけませんか") or
          check_text_terminate_string(txt, "はしてはいけないですか") or
          check_text_terminate_string(txt, "はしてはいけないか") or
          check_text_terminate_string(txt, "をやってはいけませんか") or
          check_text_terminate_string(txt, "をやってはいけないですか") or
          check_text_terminate_string(txt, "をやってはいけないか") or
          check_text_terminate_string(txt, "をやっちゃ駄目か") or
          check_text_terminate_string(txt, "をやっちゃだめか") or
          check_text_terminate_string(txt, "をやっちゃダメか") or
          check_text_terminate_string(txt, "をしちゃ駄目ですか") or
          check_text_terminate_string(txt, "をしちゃだめですか") or
          check_text_terminate_string(txt, "をしちゃダメですか") or
          check_text_terminate_string(txt, "はしちゃ駄目ですか") or
          check_text_terminate_string(txt, "はしちゃだめですか") or
          check_text_terminate_string(txt, "はしちゃダメですか") or
          check_text_terminate_string(txt, "をしちゃ駄目か") or
          check_text_terminate_string(txt, "をしちゃだめか") or
          check_text_terminate_string(txt, "をしちゃダメか") or
          check_text_terminate_string(txt, "はしちゃ駄目か") or
          check_text_terminate_string(txt, "はしちゃだめか") or
          check_text_terminate_string(txt, "はしちゃダメか") or
          check_text_terminate_string(txt, "しちゃ駄目か") or
          check_text_terminate_string(txt, "しちゃだめか") or
          check_text_terminate_string(txt, "しちゃダメか")):
           extrctd_intnt = "疑義＆質問＆確認:禁止や制限事項について"
    elif (check_text_terminate_string(txt, "がしてはいけませんか") or
          check_text_terminate_string(txt, "がしてはいけないか") or
          check_text_terminate_string(txt, "がやってはいけないか") or
          check_text_terminate_string(txt, "がやっちゃ駄目か") or
          check_text_terminate_string(txt, "がやっちゃだめか") or
          check_text_terminate_string(txt, "がやっちゃダメか") or
          check_text_terminate_string(txt, "がしちゃ駄目か") or
          check_text_terminate_string(txt, "がしちゃだめか") or
          check_text_terminate_string(txt, "がしちゃダメか")):
           extrctd_intnt = "疑義＆質問＆確認:禁止や制限事項について,特定個人についてのみ"
    elif (check_text_terminate_string(txt, "をして下さい") or
          check_text_terminate_string(txt, "をしてください") or
          check_text_terminate_string(txt, "をしてくれ") or
          check_text_terminate_string(txt, "をして") or
          check_text_terminate_string(txt, "はして下さい") or
          check_text_terminate_string(txt, "はしてください") or
          check_text_terminate_string(txt, "して下さい") or
          check_text_terminate_string(txt, "してください") or
          check_text_terminate_string(txt, "下さい") or
          check_text_terminate_string(txt, "ください") or
          check_text_terminate_string(txt, "はしてくれ") or
          check_text_terminate_string(txt, "はして") or 
          check_text_terminate_string(txt, "してくれ") or
          check_text_terminate_string(txt, "くれ")):
           extrctd_intnt = "依頼＆要求"
    elif (check_text_terminate_string(txt, "がして下さい") or
          check_text_terminate_string(txt, "がしてください") or
          check_text_terminate_string(txt, "がしてくれ") or
          check_text_terminate_string(txt, "がして")):
           extrctd_intnt = "依頼＆要求:特定個人についてのみ"
    elif (check_text_terminate_string(txt, "をして下さいますか") or
          check_text_terminate_string(txt, "をしてくださいますか") or
          check_text_terminate_string(txt, "して下さいますか") or
          check_text_terminate_string(txt, "してくださいますか") or
          check_text_terminate_string(txt, "下さいますか") or
          check_text_terminate_string(txt, "くださいますか") or
          check_text_terminate_string(txt, "をしてくれますか") or
          check_text_terminate_string(txt, "をしてくれますか") or
          check_text_terminate_string(txt, "はしてくれますか") or
          check_text_terminate_string(txt, "くれますか") or
          check_text_terminate_string(txt, "してくれるか") or
          check_text_terminate_string(txt, "くれるか") or
          check_text_terminate_string(txt, "をやって下さいますか") or
          check_text_terminate_string(txt, "をやってくださいますか") or
          check_text_terminate_string(txt, "をやってくれますか") or
          check_text_terminate_string(txt, "をやってくれるか") or
          check_text_terminate_string(txt, "はやって下さいますか") or
          check_text_terminate_string(txt, "はやってくださいますか") or
          check_text_terminate_string(txt, "はやってくれますか") or
          check_text_terminate_string(txt, "はやってくれるか")):
           extrctd_intnt = "疑義＆質問＆確認:依頼や要求について"
    elif (check_text_terminate_string(txt, "がして下さいますか") or
          check_text_terminate_string(txt, "がしてくださいますか") or
          check_text_terminate_string(txt, "がしてくれますか") or
          check_text_terminate_string(txt, "がやってくれますか") or
          check_text_terminate_string(txt, "がやってくれるか")):
           extrctd_intnt = "疑義＆質問＆確認:依頼や要求について,特定個人についてのみ"
    elif (check_text_terminate_string(txt, "がして下さいますか") or
          check_text_terminate_string(txt, "がしてくださいますか") or
          check_text_terminate_string(txt, "がしてくれますか") or
          check_text_terminate_string(txt, "がやってくれますか") or
          check_text_terminate_string(txt, "がやってくれるか")):
           extrctd_intnt = "疑義＆質問＆確認:依頼や要求について,特定個人についてのみ"
    elif (check_text_terminate_string(txt, "をお願い致します") or
          check_text_terminate_string(txt, "をお願いいたします") or
          check_text_terminate_string(txt, "をお願いします") or
          check_text_terminate_string(txt, "をお願い")):
           extrctd_intnt = "依頼＆依願"
    elif (check_text_terminate_string(txt, "しいです") or
          check_text_terminate_string(txt, "しい")):
           extrctd_intnt = "紹介＆説明＆提示:形容的"
    elif check_text_terminate_string(txt, "った"):
           extrctd_intnt = "紹介＆説明＆提示:過去形,現在完了形"
    elif (check_text_terminate_string(txt, "ったか") or
          check_text_terminate_string(txt, "ったろ")):
           extrctd_intnt = "疑義＆質問＆確認:過去形,現在完了形"
    elif check_text_terminate_string(txt, "だ"):
           extrctd_intnt = "宣言＆表明＆紹介＆説明＆提示:誇示や顕示して"
    elif (check_text_terminate_string(txt, "でしょう") or
          check_text_terminate_string(txt, "だろう") or
          check_text_terminate_string(txt, "だろ")):
           extrctd_intnt = "推定＆推測＆推量:肯定形"
    elif (check_text_terminate_string(txt, "ではないでしょう") or
          check_text_terminate_string(txt, "ではないだろう") or
          check_text_terminate_string(txt, "ではないだろ")):
           extrctd_intnt = "推定＆推測＆推量:否定形"
    elif (check_text_terminate_string(txt, "でしょうか") or
          check_text_terminate_string(txt, "だろうか") or
          check_text_terminate_string(txt, "だろか")):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,推定・推測や推量について"
    elif (check_text_terminate_string(txt, "ではないでしょうか") or
          check_text_terminate_string(txt, "ではないだろうか") or
          check_text_terminate_string(txt, "ではないだろか")):
           extrctd_intnt = "疑義＆質問＆確認:否定形,推定・推測や推量について"
    elif (check_text_terminate_string(txt, "だそうです") or
          check_text_terminate_string(txt, "だそう")):
           extrctd_intnt = "報告＆連絡:肯定形,推定・推測や推量して"
    elif (check_text_terminate_string(txt, "ではないそうです") or
          check_text_terminate_string(txt, "ではないそう")):
           extrctd_intnt = "報告＆連絡:否定形,推定・推測や推量して"
    elif (check_text_terminate_string(txt, "はいます") or
          check_text_terminate_string(txt, "はいる")):
           extrctd_intnt = "報告＆連絡:肯定形,存在の有無について"
    elif (check_text_terminate_string(txt, "がいます") or
          check_text_terminate_string(txt, "がいる")):
           extrctd_intnt = "報告＆連絡:肯定形,存在の有無について,特定の個人や個物についてのみ"
    elif (check_text_terminate_string(txt, "はいません") or
          check_text_terminate_string(txt, "はいない")):
           extrctd_intnt = "報告＆連絡:否定形,存在の有無について"
    elif (check_text_terminate_string(txt, "がいません") or
          check_text_terminate_string(txt, "がいない")):
           extrctd_intnt = "報告＆連絡:否定形,存在の有無について,特定の個人や個物についてのみ"
    elif (check_text_terminate_string(txt, "はいますか") or
          check_text_terminate_string(txt, "はいるか")):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,存在の有無について"
    elif (check_text_terminate_string(txt, "がいますか") or
          check_text_terminate_string(txt, "がいるか")):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,存在の有無について,特定の個人や個物についてのみ"
    elif (check_text_terminate_string(txt, "はいませんか") or
          check_text_terminate_string(txt, "はいないか")):
           extrctd_intnt = "疑義＆質問＆確認:否定形,存在の有無について"
    elif (check_text_terminate_string(txt, "がいませんか") or
          check_text_terminate_string(txt, "がいないか")):
           extrctd_intnt = "疑義＆質問＆確認:否定形,存在の有無について,特定の個人や個物についてのみ"
    elif (check_text_terminate_string(txt, "にいます") or
          check_text_terminate_string(txt, "にいる")):
           extrctd_intnt = "報告＆連絡:肯定形,所在や場所について"
    elif (check_text_terminate_string(txt, "にいません") or
          check_text_terminate_string(txt, "にいない")):
           extrctd_intnt = "報告＆連絡:否定形,所在や場所について"
    elif (check_text_terminate_string(txt, "はあります") or
          check_text_terminate_string(txt, "はある")):
           extrctd_intnt = "報告＆連絡:肯定形,存在の有無について"
    elif (check_text_terminate_string(txt, "があります") or
          check_text_terminate_string(txt, "がある")):
           extrctd_intnt = "報告＆連絡:肯定形,存在の有無について,特定の個人や個物についてのみ"
    elif (check_text_terminate_string(txt, "はありません") or
          check_text_terminate_string(txt, "はない")):
           extrctd_intnt = "報告＆連絡:否定形,存在の有無について"
    elif (check_text_terminate_string(txt, "がありません") or
          check_text_terminate_string(txt, "がない")):
           extrctd_intnt = "報告＆連絡:否定形,存在の有無について,特定の個人や個物についてのみ"
    elif (check_text_terminate_string(txt, "にいますか") or
          check_text_terminate_string(txt, "にいるか")):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,存在の有無について"
    elif (check_text_terminate_string(txt, "にいませんか") or
          check_text_terminate_string(txt, "にいないか")):
           extrctd_intnt = "疑義＆質問＆確認:否定形,存在の有無について"
    elif (check_text_terminate_string(txt, "はありますか") or
          check_text_terminate_string(txt, "はあるか")):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,存在の有無について"
    elif (check_text_terminate_string(txt, "がありますか") or
          check_text_terminate_string(txt, "があるか")):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,存在の有無について,特定の個人や個物についてのみ"
    elif (check_text_terminate_string(txt, "はありませんか") or
          check_text_terminate_string(txt, "はあるか")):
           extrctd_intnt = "疑義＆質問＆確認:否定形,存在の有無について"
    elif (check_text_terminate_string(txt, "がありませんか") or
          check_text_terminate_string(txt, "がないか")):
           extrctd_intnt = "疑義＆質問＆確認:否定形,存在の有無について,特定の個人や個物についてのみ"
    elif (check_text_terminate_string(txt, "になっている") or
          check_text_terminate_string(txt, "になってある")):
           extrctd_intnt = "報告＆連絡:肯定形,存在の状態について"
    elif (check_text_terminate_string(txt, "になっていない") or
          check_text_terminate_string(txt, "になってない")):
           extrctd_intnt = "報告＆連絡:否定形,存在の状態について"
    elif (check_text_terminate_string(txt, "で御座います") or
          check_text_terminate_string(txt, "でございます") or
          check_text_terminate_string(txt, "であります") or
          check_text_terminate_string(txt, "です")):
           extrctd_intnt = "宣言＆表明＆紹介＆説明＆提示:肯定形,漠然として"
    elif (check_text_terminate_string(txt, "では御座いません") or
          check_text_terminate_string(txt, "ではございません") or
          check_text_terminate_string(txt, "ではありません") or
          check_text_terminate_string(txt, "ではないです")):
           extrctd_intnt = "宣言＆表明＆紹介＆説明＆提示:否定形,漠然として"
    elif (check_text_terminate_string(txt, "で御座いますか") or
          check_text_terminate_string(txt, "でございますか") or
          check_text_terminate_string(txt, "でありますか") or
          check_text_terminate_string(txt, "ですか")):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,漠然として"
    elif (check_text_terminate_string(txt, "では御座いませんか") or
          check_text_terminate_string(txt, "ではございませんか") or
          check_text_terminate_string(txt, "ではありませんか") or
          check_text_terminate_string(txt, "ではないですか")):
           extrctd_intnt = "疑義＆質問＆確認:否定形,漠然として"
    elif (check_text_terminate_string(txt, "で御座いましたか") or
          check_text_terminate_string(txt, "でございましたか") or
          check_text_terminate_string(txt, "でありましたか") or
          check_text_terminate_string(txt, "でしたか") or
          check_text_terminate_string(txt, "だったか")):
           extrctd_intnt = "疑義＆質問＆確認:過去,肯定形,状況や状態について,物事の進行や進捗について"
    elif (check_text_terminate_string(txt, "という事で御座います") or
          check_text_terminate_string(txt, "という事でございます") or
          check_text_terminate_string(txt, "ということで御座います") or
          check_text_terminate_string(txt, "ということでございます") or
          check_text_terminate_string(txt, "という事であります") or
          check_text_terminate_string(txt, "ということであります") or
          check_text_terminate_string(txt, "という事です") or
          check_text_terminate_string(txt, "ということです") or
          check_text_terminate_string(txt, "って事です") or
          check_text_terminate_string(txt, "ってことです")):
           extrctd_intnt = "紹介＆説明＆提示:肯定形,なんらかの内容についての叙述"
    elif (check_text_terminate_string(txt, "という事では御座いません") or
          check_text_terminate_string(txt, "という事ではございません") or
          check_text_terminate_string(txt, "ということでは御座いません") or
          check_text_terminate_string(txt, "ということではございません") or
          check_text_terminate_string(txt, "という事ではありません") or
          check_text_terminate_string(txt, "ということではありません") or
          check_text_terminate_string(txt, "って事ではないです") or
          check_text_terminate_string(txt, "ってことではないです")):
           extrctd_intnt = "紹介＆説明＆提示:否定形,なんらかの内容についての叙述"
    elif (check_text_terminate_string(txt, "という事で御座いますか") or
          check_text_terminate_string(txt, "という事でございますか") or
          check_text_terminate_string(txt, "ということで御座いますか") or
          check_text_terminate_string(txt, "ということでございますか") or
          check_text_terminate_string(txt, "という事でありますか") or
          check_text_terminate_string(txt, "ということでありますか") or
          check_text_terminate_string(txt, "という事ですか") or
          check_text_terminate_string(txt, "ということですか") or
          check_text_terminate_string(txt, "って事ですか") or
          check_text_terminate_string(txt, "ってことですか")):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,なんらかの内容についての叙述"
    elif (check_text_terminate_string(txt, "という事では御座いませんか") or
          check_text_terminate_string(txt, "という事ではございませんか") or
          check_text_terminate_string(txt, "ということでは御座いませんか") or
          check_text_terminate_string(txt, "ということではございませんか") or
          check_text_terminate_string(txt, "という事ではありませんか") or
          check_text_terminate_string(txt, "ということではありませんか") or
          check_text_terminate_string(txt, "って事ではないのですか") or
          check_text_terminate_string(txt, "ってことではなのですか") or
          check_text_terminate_string(txt, "って事ではないんですか") or
          check_text_terminate_string(txt, "ってことではないんですか")):
           extrctd_intnt = "疑義＆質問＆確認:否定形,なんらかの内容についての叙述"
    elif (check_text_terminate_string(txt, "は大丈夫です") or
          check_text_terminate_string(txt, "は大丈夫だ") or
          check_text_terminate_string(txt, "は大丈夫")):
           extrctd_intnt = "宣言＆表明:肯定形,安否や健康状態について"
    elif (check_text_terminate_string(txt, "は大丈夫ではない") or
          check_text_terminate_string(txt, "は大丈夫でない") or
          check_text_terminate_string(txt, "は大丈夫じゃない")):
           extrctd_intnt = "宣言＆表明:否定形,安否や健康状態について"
    elif (check_text_terminate_string(txt, "は大丈夫でしょうか") or
          check_text_terminate_string(txt, "は大丈夫ですか") or
          check_text_terminate_string(txt, "は大丈夫か")):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,安否や健康状態について"
    elif (check_text_terminate_string(txt, "は大丈夫ではないのでしょうか") or
          check_text_terminate_string(txt, "は大丈夫ではないんですか") or
          check_text_terminate_string(txt, "は大丈夫じゃないんですか")):
           extrctd_intnt = "疑義＆質問＆確認:否定形,安否や健康状態について"
    elif (check_text_terminate_string(txt, "が必要です") or
          check_text_terminate_string(txt, "は必要です") or
          check_text_terminate_string(txt, "が必要だ") or
          check_text_terminate_string(txt, "は必要だ") or
          check_text_terminate_string(txt, "が必要") or
          check_text_terminate_string(txt, "は必要") or
          check_text_terminate_string(txt, "が要ります") or
          check_text_terminate_string(txt, "は要ります") or
          check_text_terminate_string(txt, "が要る") or
          check_text_terminate_string(txt, "は要る")):
           extrctd_intnt = "宣言＆表明:肯定形,物事の要否について"
    elif (check_text_terminate_string(txt, "が不要です") or
          check_text_terminate_string(txt, "は不要です") or
          check_text_terminate_string(txt, "が不要だ") or
          check_text_terminate_string(txt, "は不要だ") or
          check_text_terminate_string(txt, "が不要") or
          check_text_terminate_string(txt, "は不要") or
          check_text_terminate_string(txt, "が要りません") or
          check_text_terminate_string(txt, "は要りません") or
          check_text_terminate_string(txt, "が要らない") or
          check_text_terminate_string(txt, "は要らない")):
           extrctd_intnt = "宣言＆表明:否定形,物事の要否について"
    elif (check_text_terminate_string(txt, "が必要でしょうか") or
          check_text_terminate_string(txt, "は必要でしょうか") or
          check_text_terminate_string(txt, "が必要ですか") or
          check_text_terminate_string(txt, "は必要ですか") or
          check_text_terminate_string(txt, "が要りますでしょうか") or
          check_text_terminate_string(txt, "は要りますでしょうか") or
          check_text_terminate_string(txt, "が要りますか") or
          check_text_terminate_string(txt, "は要りますか")):
           extrctd_intnt = "疑義＆質問＆確認:肯定形,物事の要否について"
    elif (check_text_terminate_string(txt, "が不要でしょうか") or
          check_text_terminate_string(txt, "は不要でしょうか") or
          check_text_terminate_string(txt, "が不要ですか") or
          check_text_terminate_string(txt, "は不要ですか") or
          check_text_terminate_string(txt, "が要りませんか") or
          check_text_terminate_string(txt, "は要りませんか") or
          check_text_terminate_string(txt, "が要らないのですか") or
          check_text_terminate_string(txt, "は要らないのですか") or
          check_text_terminate_string(txt, "が要らないのか") or
          check_text_terminate_string(txt, "は要らないのか") or
          check_text_terminate_string(txt, "が要らないか") or
          check_text_terminate_string(txt, "は要らないか")):
           extrctd_intnt = "疑義＆質問＆確認:否定形,物事の要否について"
    elif (check_text_terminate_string(txt, "という事でしょう") or
          check_text_terminate_string(txt, "ということでしょう")):
           extrctd_intnt = "推定＆推測＆推量:肯定形,進言や提言に近い"
    elif (check_text_terminate_string(txt, "という事ではないでしょう") or
          check_text_terminate_string(txt, "ということではないでしょう")):
           extrctd_intnt = "推定＆推測＆推量:否定形,進言や提言に近い"
    elif (check_text_terminate_string(txt, "かも知れないです") or
          check_text_terminate_string(txt, "かもしれないです") or
          check_text_terminate_string(txt, "かも知れない") or
          check_text_terminate_string(txt, "かもしれない")):
           extrctd_intnt = "推定＆推測＆推量:肯定形"
    elif (check_text_terminate_string(txt, "ではないかも知れないです") or
          check_text_terminate_string(txt, "ではないかもしれないです") or
          check_text_terminate_string(txt, "ではないかも知れない") or
          check_text_terminate_string(txt, "ではないかもしれない")):
           extrctd_intnt = "推定＆推測＆推量:否定形"
    elif (check_text_terminate_string(txt, "かと存じ上げます") or
          check_text_terminate_string(txt, "と存じます") or
          check_text_terminate_string(txt, "かと思います") or
          check_text_terminate_string(txt, "と思います")):
           extrctd_intnt = "既知＆認知:肯定形"
    elif (check_text_terminate_string(txt, "とは存じ上げませんでした") or
          check_text_terminate_string(txt, "と存じまませんでした") or
          check_text_terminate_string(txt, "とは思いません") or
          check_text_terminate_string(txt, "と思いません")):
           extrctd_intnt = "既知＆認知:否定形"
    elif (check_text_terminate_string(txt, "とは思っています") or
          check_text_terminate_string(txt, "とは思ってます") or
          check_text_terminate_string(txt, "とは思っている") or
          check_text_terminate_string(txt, "とは思ってる") or
          check_text_terminate_string(txt, "とは思う") or
          check_text_terminate_string(txt, "と思っています") or
          check_text_terminate_string(txt, "と思ってます") or
          check_text_terminate_string(txt, "と思っている") or
          check_text_terminate_string(txt, "と思ってる") or
          check_text_terminate_string(txt, "と思う")):
           extrctd_intnt = "思慮＆考慮:現在,肯定形"
    elif (check_text_terminate_string(txt, "とは思っていません") or
          check_text_terminate_string(txt, "とは思ってません") or
          check_text_terminate_string(txt, "とは思っていない") or
          check_text_terminate_string(txt, "とは思ってない") or
          check_text_terminate_string(txt, "とは思わない") or
          check_text_terminate_string(txt, "と思っていません") or
          check_text_terminate_string(txt, "と思ってません") or
          check_text_terminate_string(txt, "と思っていない") or
          check_text_terminate_string(txt, "と思ってない") or
          check_text_terminate_string(txt, "と思わない")):
           extrctd_intnt = "思慮＆考慮:現在,否定形"
    elif (check_text_terminate_string(txt, "とは思っていました") or
          check_text_terminate_string(txt, "とは思ってました") or
          check_text_terminate_string(txt, "とは思っていた") or
          check_text_terminate_string(txt, "とは思ってた") or
          check_text_terminate_string(txt, "と思っていました") or
          check_text_terminate_string(txt, "と思ってました") or
          check_text_terminate_string(txt, "と思っていた") or
          check_text_terminate_string(txt, "と思ってた")):
           extrctd_intnt = "思慮＆考慮:過去,肯定形"
    elif (check_text_terminate_string(txt, "とは思っていませんでした") or
          check_text_terminate_string(txt, "とは思っていなかった") or
          check_text_terminate_string(txt, "とは思ってなかった") or
          check_text_terminate_string(txt, "と思っていませんでした") or
          check_text_terminate_string(txt, "と思っていなかった") or
          check_text_terminate_string(txt, "と思ってなかった")):
           extrctd_intnt = "思慮＆考慮:過去,否定形"
    elif (check_text_terminate_string(txt, "について考えて参ります") or
          check_text_terminate_string(txt, "について考えてまいります") or
          check_text_terminate_string(txt, "について考えて行きます") or
          check_text_terminate_string(txt, "について考えていきます") or
          check_text_terminate_string(txt, "について考えます") or
          check_text_terminate_string(txt, "を考えます") or
          check_text_terminate_string(txt, "が考えます") or
          check_text_terminate_string(txt, "は考えます")):
           extrctd_intnt = "感想＆感慨:否定形,形容的な表現"
    elif (check_text_terminate_string(txt, "と申します") or
          check_text_terminate_string(txt, "と言います")):
           extrctd_intnt = "感想＆感慨:否定形,形容的な表現"
    elif (check_text_terminate_string(txt, "らしいです") or
          check_text_terminate_string(txt, "らしい")):
           extrctd_intnt = "感想＆感慨:肯定形,形容的な表現"
    elif (check_text_terminate_string(txt, "らしくないです") or
          check_text_terminate_string(txt, "らしくない")):
           extrctd_intnt = "感想＆感慨:否定形,形容的な表現"
    elif (check_text_terminate_string(txt, "とは何でしょうか") or
          check_text_terminate_string(txt, "とはなんでしょうか") or
          check_text_terminate_string(txt, "とは何ですか") or
          check_text_terminate_string(txt, "とはなんですか") or
          check_text_terminate_string(txt, "とは何なのか") or
          check_text_terminate_string(txt, "とはなんなのか") or
          check_text_terminate_string(txt, "とは何か") or
          check_text_terminate_string(txt, "とはなにか") or
          check_text_terminate_string(txt, "とは何") or
          check_text_terminate_string(txt, "とはなに") or
          check_text_terminate_string(txt, "とは") or
          check_text_terminate_string(txt, "って何") or
          check_text_terminate_string(txt, "ってなに") or
          check_text_terminate_string(txt, "って")):
           extrctd_intnt = "単純質問"
    elif (check_text_terminate_string(txt, "でございます") or
          check_text_terminate_string(txt, "にございます") or
          check_text_terminate_string(txt, "となります") or
          check_text_terminate_string(txt, "になります")):
           extrctd_intnt = "紹介＆提示＆説明:単純"
    elif (check_text_terminate_string(txt, "にありまして") or
          check_text_terminate_string(txt, "におりまして") or
          check_text_terminate_string(txt, "がありまして") or
          check_text_terminate_string(txt, "がおりまして")):
           extrctd_intnt = "申告＆申立て"
    elif (check_text_terminate_string(txt, "ですので") or
          check_text_terminate_string(txt, "なので") or
          check_text_terminate_string(txt, "ので")):
           extrctd_intnt = "説得＆説明"
    elif (check_text_terminate_string(txt, "という事でして") or
          check_text_terminate_string(txt, "ということでして") or
          check_text_terminate_string(txt, "という事で") or
          check_text_terminate_string(txt, "ということで") or
          check_text_terminate_string(txt, "って事で") or
          check_text_terminate_string(txt, "ってことで")):
           extrctd_intnt = "説得＆説明:言い訳に近い"
    elif (check_text_terminate_string(txt, "なものでして") or
          check_text_terminate_string(txt, "なもので") or
          check_text_terminate_string(txt, "でして")):
           extrctd_intnt = "説得＆説明:言い訳に近い"
    else:
           extrctd_intnt     = "不明・その他"
           extrctd_intnt_txt = txt


    return extrctd_intnt, extrctd_intnt_txt


#テキストからコンテント(＝主語と述語の組,インテントに付随する内容)を抽出する
def extract_content(txt):

    rmvd_symbl_txt     = remove_symbols(txt)
    rmvd_emoji_txt     = remove_emoji(rmvd_symbl_txt)
    rmvd_emotnl_txt    = remove_emotional(rmvd_emoji_txt)
    rmvd_fnl_prtcl_txt = remove_final_particle(rmvd_emotnl_txt)
    rmvd_1st_cnnct_txt = remove_1st_connect(rmvd_fnl_prtcl_txt)
    rmvd_2nd_cnnct_txt = remove_2nd_connect(rmvd_1st_cnnct_txt)
    extrctd_cntnt_txt  = rmvd_2nd_cnnct_txt

    tkns  = token_analyze2(extrctd_cntnt_txt)

    tkns = join_tokens_by_noun(tkns)
    tkns = join_tokens_by_noun_between_jp_no(tkns)
    tkns = join_tokens_by_verb_and_auxiliary_verb(tkns)
    tkns = join_tokens_by_verbs_and_conjunctive_particle(tkns)
    tkns = join_tokens_by_verbs_conjunctive_particle_and_verbs(tkns)
    tkns = join_tokens_by_jp_to_as_case_particle_and_jp_ha_as_participant_particle(tkns)

    extrctd_cntnt = extract_content_with_jp_toha(tkns)

    if extrctd_cntnt == "主語: 述語: (文型不一致)":
       extrctd_cntnt = extract_content_with_jp_to_toha(tkns)
    if extrctd_cntnt == "主語: 述語: (文型不一致)":
       extrctd_cntnt = extract_content_with_jp_to_ha(tkns)
    if extrctd_cntnt == "主語: 述語: (文型不一致)":
       extrctd_cntnt = extract_content_with_jp_to_ga(tkns)
    if extrctd_cntnt == "主語: 述語: (文型不一致)":
       extrctd_cntnt = extract_content_with_jp_to_mo(tkns)
    if extrctd_cntnt == "主語: 述語: (文型不一致)":
       extrctd_cntnt = extract_content_with_jp_ya_ha(tkns)
    if extrctd_cntnt == "主語: 述語: (文型不一致)":
       extrctd_cntnt = extract_content_with_jp_ya_ga(tkns)
    if extrctd_cntnt == "主語: 述語: (文型不一致)":
       extrctd_cntnt = extract_content_with_jp_ya_mo(tkns)
    if extrctd_cntnt == "主語: 述語: (文型不一致)":
       extrctd_cntnt = extract_content_with_jp_ha(tkns)
    if extrctd_cntnt == "主語: 述語: (文型不一致)":
       extrctd_cntnt = extract_content_with_jp_ga(tkns)
    if extrctd_cntnt == "主語: 述語: (文型不一致)":
       extrctd_cntnt = extract_content_with_jp_mo(tkns)


    return extrctd_cntnt, extrctd_cntnt_txt


#新旧数件分のテキストからトピック(＝話題,文脈の中心)を抽出する
def extract_topic(new_txt, old_txt, old_txt2, old_txt3, old_txt4):
    tknzr      = Tokenizer()
    tkns       = tknzr.tokenize(new_txt + old_txt + old_txt2 + old_txt3 + old_txt4)
    anlyzd_txt = []
    wrds       = {}
    tkns_idx    = 0


    for tkn in tkns:
        anlyzd_txt.append([tkn.surface, tkn.part_of_speech])

    while tkns_idx < len(anlyzd_txt):
          if "名詞" in anlyzd_txt[tkns_idx][1] or "動詞" in anlyzd_txt[tkns_idx][1]:
             wrds[anlyzd_txt[tkns_idx][0]] += 1

          tkns_idx += 1

    tpc = max(wrds, key=wrds.get)

    return tpc


#テキストの中の連続して現れる名詞同士を結合する
def join_tokens_by_noun(tkns):
    joind_tkns = []
    tkns_seq   = ""
    tkns_idx   = 0
    tkns_cnt   = 0


    while tkns_idx < len(tkns):
          if ("名詞" in tkns[tkns_idx][1] and tkns_seq == ""):
              tkns_seq += tkns[tkns_idx][0]
              print(tkns_seq+"1")
              print(joind_tkns)
              tkns_cnt += 1
              tkns_idx += 1
              continue

          if ("名詞" not in tkns[tkns_idx][1] and tkns_seq == ""):
              joind_tkns.append([tkns[tkns_idx][0], tkns[tkns_idx][1]])
              print(tkns_seq+"2")
              print(joind_tkns)
              tkns_idx += 1
              continue

          if ("名詞" in tkns[tkns_idx][1] and tkns_seq != ""):
              tkns_seq += tkns[tkns_idx][0]
              print(tkns_seq+"3")
              print(joind_tkns)
              tkns_cnt += 1
              tkns_idx += 1
              continue

          if ("名詞" not in tkns[tkns_idx][1] and tkns_seq != ""):
              if   tkns_cnt < 2:
                   joind_tkns.append([tkns_seq, "名詞,一般,固有,*"])
              else:
                   joind_tkns.append([tkns_seq, "名詞,一般,固有,連結＆連体"])

              joind_tkns.append([tkns[tkns_idx][0], tkns[tkns_idx][1]])
              print(tkns_seq+"4")
              print(joind_tkns)
              tkns_seq = ""
              tkns_cnt = 0
              tkns_idx += 1
              continue

          tkns_idx += 1
          continue

    else:

          if tkns_seq != "":
             anlyzd_txt = token_analyze2(tkns_seq)

             if   "名詞" in anlyzd_txt[0][1]:
                  joind_tkns.append([tkns_seq, "名詞,一般,固有,*"])
             else:
                  joind_tkns.append([anlyzd_txt[0][0], anlyzd_txt[0][1]])

             print(tkns_seq+"5")
             print(joind_tkns)

    return joind_tkns


#テキストの中の「の」を挟んで連続して現れる名詞同士を結合する
def join_tokens_by_noun_between_jp_no(tkns):
    joind_tkns = []
    tkns_seq   = ""
    tkns_idx   = 0
    tkns_cnt   = 0


    while tkns_idx < len(tkns):
          if ("助詞" in tkns[tkns_idx][1] and \
              tkns[tkns_idx][0] == "の" and tkns_seq == ""):
              tkns_idx += 1
              print(tkns_seq+"1")
              print(joind_tkns)
              #pass

          if ("助詞" in tkns[tkns_idx][1] and \
              tkns[tkns_idx][0] == "の" and tkns_seq != ""):
              tkns_seq += "の"
              tkns_cnt += 1
              tkns_idx += 1
              print(tkns_seq+"2")
              print(joind_tkns)
              continue

          if ("名詞" in tkns[tkns_idx][1] and tkns_seq == ""):
              tkns_seq += tkns[tkns_idx][0]
              tkns_cnt += 1
              tkns_idx += 1
              print(tkns_seq+"3")
              print(joind_tkns)
              continue

          if ("名詞" in tkns[tkns_idx][1] and tkns_seq != ""):
              tkns_seq += tkns[tkns_idx][0]
              joind_tkns.append([tkns_seq, "名詞,一般,固有,連結＆連体"])
              tkns_seq = ""
              tkns_cnt = 0
              tkns_idx += 1
              print(tkns_seq+"4")
              print(joind_tkns)
              continue

          if ("名詞" not in tkns[tkns_idx][1] and tkns_seq == ""):
              joind_tkns.append([tkns[tkns_idx][0], tkns[tkns_idx][1]])
              tkns_cnt = 0
              tkns_idx += 1
              print(tkns_seq+"5")
              print(joind_tkns)
              continue

          if ("名詞" not in tkns[tkns_idx][1] and tkns_seq != ""):
              joind_tkns.append([tkns_seq, "名詞,一般,固有,*"])
              joind_tkns.append([tkns[tkns_idx][0], tkns[tkns_idx][1]])
              tkns_seq = ""
              tkns_cnt = 0
              tkns_idx += 1
              print(tkns_seq+"6")
              print(joind_tkns)
              continue

          if ("名詞" not in tkns[tkns_idx][1] and \
              tkns[tkns_idx][0] != "の" and tkns_seq == ""):
              joind_tkns.append([tkns[tkns_idx][0], tkns[tkns_idx][1]])
              tkns_cnt = 0
              tkns_idx += 1
              print(tkns_seq+"7")
              print(joind_tkns)
              continue

          if ("名詞" not in tkns[tkns_idx][1] and \
              tkns[tkns_idx][0] != "の" and tkns_seq != ""):
              if   tkns_cnt < 2:
                   joind_tkns.append([tkns_seq, "名詞,一般,固有,*"])
              else:
                   joind_tkns.append([tkns_seq, "名詞,一般,固有,連結＆連体"])

              joind_tkns.append([tkns[tkns_idx][0], tkns[tkns_idx][1]])
              print(tkns_seq+"8")
              print(joind_tkns)
              tkns_seq = ""
              tkns_cnt = 0
              tkns_idx += 1
              continue

          tkns_idx += 1
          continue

    else:

          if tkns_seq != "":
             anlyzd_txt = token_analyze2(tkns_seq)

             if   "名詞" in anlyzd_txt[0][1]:
                  joind_tkns.append([tkns_seq, "名詞,一般,固有,*"])
             else:
                  joind_tkns.append([anlyzd_txt[0][0], anlyzd_txt[0][1]])

             print(tkns_seq+"9")
             print(joind_tkns)

    return joind_tkns


#テキストの中の連続して現れる動詞と(助)動詞を結合する
def join_tokens_by_verb_and_auxiliary_verb(tkns):
    joind_tkns = []
    tkns_seq   = ""
    tkns_idx   = 0


    while tkns_idx < len(tkns):
          if ("動詞" in tkns[tkns_idx][1] and tkns_seq == ""):
              tkns_seq += tkns[tkns_idx][0]
              tkns_idx += 1
              print(tkns_seq+"1")
              print(joind_tkns)
              continue

          if ("動詞" not in tkns[tkns_idx][1] and tkns_seq == ""):
              joind_tkns.append([tkns[tkns_idx][0], tkns[tkns_idx][1]])
              tkns_idx += 1
              print(tkns_seq+"2")
              print(joind_tkns)
              continue

          if ("動詞" in tkns[tkns_idx][1] and tkns_seq != ""):
              tkns_seq += tkns[tkns_idx][0]
              joind_tkns.append([tkns_seq, "動詞＋(助)動詞形,連結＆連体,*,*"])
              tkns_seq = ""
              tkns_idx += 1
              print(tkns_seq+"3")
              print(joind_tkns)
              continue

          if ("動詞" not in tkns[tkns_idx][1] and tkns_seq != ""):
              joind_tkns.append([tkns_seq, "動詞＋(助)動詞形,連結＆連体,*,*"])
              joind_tkns.append([tkns[tkns_idx][0], tkns[tkns_idx][1]])
              print(tkns_seq+"4")
              print(joind_tkns)
              tkns_seq = ""
              tkns_idx += 1
              continue

          tkns_idx += 1
          continue

    else:

          if tkns_seq != "":
             anlyzd_txt = token_analyze2(tkns_seq)

             if   anlyzd_txt[0][1] == "動詞,*,*,*" :
                  joind_tkns.append([tkns_seq, "(助)動詞,*,*,*"])
             else:
                  joind_tkns.append([anlyzd_txt[0][0], anlyzd_txt[0][1]])

             print(tkns_seq+"5")
             print(joind_tkns)

    return joind_tkns


#テキストの中の連続して現れる「動詞＋(助)動詞形」と接続助詞を結合する
def join_tokens_by_verbs_and_conjunctive_particle(tkns):
    joind_tkns = []
    tkns_seq   = ""
    tkns_idx   = 0


    while tkns_idx < len(tkns):
          if (("接続助詞" in tkns[tkns_idx][1] or \
               "動詞＋(助)動詞形" in tkns[tkns_idx][1]) and tkns_seq == ""):
               if "接続助詞" in tkns[tkns_idx][1]:
                  tkns_idx += 1
                  print(tkns_seq+"1")
                  print(joind_tkns)
                  continue
                  #pass

               if "動詞＋(助)動詞形" in tkns[tkns_idx][1]:
                  tkns_seq += tkns[tkns_idx][0]
                  tkns_idx += 1
                  print(tkns_seq+"2")
                  print(joind_tkns)
                  continue

          if (("接続助詞" in tkns[tkns_idx][1] or \
               "動詞＋(助)動詞形" in tkns[tkns_idx][1]) and tkns_seq != ""):
               if "接続助詞" in tkns[tkns_idx][1]:
                  tkns_seq += tkns[tkns_idx][0]
                  joind_tkns.append([tkns_seq, "動詞＋(助)動詞＋接続助詞形,連結＆連体,*,*"])
                  tkns_seq = ""
                  tkns_idx += 1
                  print(tkns_seq+"3")
                  print(joind_tkns)
                  continue
                  #pass

               if "動詞＋(助)動詞形" in tkns[tkns_idx][1]:
                  tkns_idx += 1
                  print(tkns_seq+"4")
                  print(joind_tkns)
                  continue

          if (("接続助詞" not in tkns[tkns_idx][1] and \
               "動詞＋(助)動詞形" not in tkns[tkns_idx][1]) and tkns_seq == ""):
               joind_tkns.append([tkns[tkns_idx][0], tkns[tkns_idx][1]])
               tkns_idx += 1
               print(tkns_seq+"5")
               print(joind_tkns)
               continue

          if (("接続助詞" not in tkns[tkns_idx][1] and \
               "動詞＋(助)動詞形" not in tkns[tkns_idx][1]) and tkns_seq != ""):
               joind_tkns.append([tkns_seq, "動詞＋(助)動詞形,連結＆連体,*,*"])
               joind_tkns.append([tkns[tkns_idx][0], tkns[tkns_idx][1]])
               print(tkns_seq+"6")
               print(joind_tkns)
               tkns_seq = ""
               tkns_idx += 1
               continue
               #pass

          tkns_idx += 1
          continue

    else:

          if tkns_seq != "":
             anlyzd_txt = token_analyze2(tkns_seq)

             if  (anlyzd_txt[0][1] == "動詞,*,*,*" or \
                  anlyzd_txt[0][1] == "動詞,自立,*,*" or anlyzd_txt[0][1] == "動詞,非自立,*,*"):
                  joind_tkns.append([tkns_seq, "動詞＋(助)動詞形,連結＆連体,*,*"])
             else:
                  joind_tkns.append([anlyzd_txt[0][0], anlyzd_txt[0][1]])

             print(tkns_seq+"7")
             print(joind_tkns)


    return joind_tkns


#テキストの中の連続して現れる「動詞＋(助)動詞＋接続助詞形」と「動詞＋(助)動詞形」を結合する
def join_tokens_by_verbs_conjunctive_particle_and_verbs(tkns):
    joind_tkns = []
    tkns_seq    = ""
    tkns_idx    = 0


    while tkns_idx < len(tkns):
          if "動詞" in tkns[tkns_idx][1]:
             joind_tkns.append([tkns[tkns_idx][0], tkns[tkns_idx][1]])
             tkns_idx += 1
             print(tkns_seq+"1")
             print(joind_tkns)
             continue

          if (("動詞＋(助)動詞＋接続助詞形" in tkns[tkns_idx][1] or \
               "動詞＋(助)動詞形" in tkns[tkns_idx][1]) and tkns_seq == ""):
               if "動詞＋(助)動詞＋接続助詞形" in tkns[tkns_idx][1]:
                  tkns_seq += tkns[tkns_idx][0]
                  tkns_idx += 1
                  print(tkns_seq+"2")
                  print(joind_tkns)
                  continue
                  #pass

               if "動詞＋(助)動詞形" in tkns[tkns_idx][1]:
                  tkns_idx += 1
                  print(tkns_seq+"3")
                  print(joind_tkns)
                  continue

          if (("動詞＋(助)動詞＋接続助詞形" in tkns[tkns_idx][1] or \
               "動詞＋(助)動詞形" in tkns[tkns_idx][1]) and tkns_seq != ""):
               if "動詞＋(助)動詞＋接続助詞形" in tkns[tkns_idx][1]:
                  tkns_idx += 1
                  print(tkns_seq+"4")
                  print(joind_tkns)
                  continue
                  #pass

               if "動詞＋(助)動詞形" in tkns[tkns_idx][1]:
                  tkns_seq += tkns[tkns_idx][0]
                  joind_tkns.append([tkns_seq, "動詞＋(助)動詞＋接続助詞＋動詞＋(助)動詞形,連結＆連体,*,*"])
                  print(tkns_seq+"5")
                  print(joind_tkns)
                  tkns_seq = ""
                  tkns_idx += 1
                  continue

          if (("動詞＋(助)動詞＋接続助詞形" not in tkns[tkns_idx][1] and \
               "動詞＋(助)動詞形" not in tkns[tkns_idx][1]) and tkns_seq == ""):
               joind_tkns.append([tkns[tkns_idx][0], tkns[tkns_idx][1]])
               tkns_idx += 1
               print(tkns_seq+"6")
               print(joind_tkns)
               continue

          if (("動詞＋(助)動詞＋接続助詞形" not in tkns[tkns_idx][1] and \
               "動詞＋(助)動詞形" not in tkns[tkns_idx][1]) and tkns_seq != ""):
               joind_tkns.append([tkns_seq, "動詞＋(助)動詞＋接続助詞形,連結＆連体,*,*"])
               joind_tkns.append([tkns[tkns_idx][0], tkns[tkns_idx][1]])
               print(tkns_seq+"7")
               print(joind_tkns)
               tkns_seq = ""
               tkns_idx += 1
               continue
               #pass

          tkns_idx += 1
          continue

    else:

          if tkns_seq != "":
             anlyzd_txt = token_analyze2(tkns_seq)

             if   anlyzd_txt[0][1] == "動詞,*,*,*" :
                  joind_tkns.append([tkns_seq, "動詞＋(助)動詞＋接続助詞形,連結＆連体,*,*"])
             else:
                  joind_tkns.append([anlyzd_txt[0][0], anlyzd_txt[0][1]])

             print(tkns_seq+"8")
             print(joind_tkns)


    return joind_tkns


#テキストの中の連続して現れる格助詞(＝「と」)と係助詞(＝「は」)を結合する
def join_tokens_by_jp_to_as_case_particle_and_jp_ha_as_participant_particle(tkns):
    joind_tkns = []
    tkns_seq   = ""
    tkns_idx   = 0


    while tkns_idx < len(tkns):
          if ("格助詞" in tkns[tkns_idx][1] and \
              tkns[tkns_idx][0] == "と" and tkns_seq == ""):
              tkns_seq += "と" 
              print(tkns_seq+"1")
              print(joind_tkns)
              tkns_idx += 1
              continue
              #pass

          if ("格助詞" not in tkns[tkns_idx][1] and tkns_seq == ""):
              joind_tkns.append([tkns[tkns_idx][0], tkns[tkns_idx][1]])
              print(tkns_seq+"2")
              print(joind_tkns)
              tkns_idx += 1
              continue

          if ("格助詞" in tkns[tkns_idx][1] and \
              tkns[tkns_idx][0] == "と" and tkns_seq != ""):
              print(tkns_seq+"3")
              print(joind_tkns)
              tkns_idx += 1
              continue

          if ("格助詞" not in tkns[tkns_idx][1] and tkns_seq != ""):
              if ("係助詞" in tkns[tkns_idx][1] and tkns[tkns_idx][0] == "は"):
                  tkns_seq += tkns[tkns_idx][0]
                  joind_tkns.append([tkns_seq, "格助詞＋係助詞形,連結＆連体,*,*"])
                  print(tkns_seq+"4")
                  print(joind_tkns)
                  tkns_seq = ""
                  tkns_idx += 1
                  continue

          if ("係助詞" in tkns[tkns_idx][1] and \
              tkns[tkns_idx][0] == "は" and tkns_seq == ""):
              print(tkns_seq+"5")
              print(joind_tkns)
              tkns_idx += 1
              continue

          if ("係助詞" not in tkns[tkns_idx][1] and tkns_seq == ""):
              joind_tkns.append([tkns[tkns_idx][0], tkns[tkns_idx][1]])
              print(tkns_seq+"6")
              print(joind_tkns)
              tkns_idx += 1
              continue

          if ("係助詞" in tkns[tkns_idx][1] and \
              tkns[tkns_idx][0] == "は" and tkns_seq != ""):
              tkns_seq += tkns[tkns_idx][0]
              joind_tkns.append([tkns_seq, "格助詞＋係助詞形,連結＆連体,*,*"])
              print(tkns_seq+"7")
              print(joind_tkns)
              tkns_seq = ""
              tkns_idx += 1
              continue

          if ("係助詞" not in tkns[tkns_idx][1] and tkns_seq != ""):
              print(tkns_seq+"8")
              print(joind_tkns)
              tkns_idx += 1
              continue

          tkns_idx += 1
          continue

    else:

          if tkns_seq != "":
             anlyzd_txt = token_analyze2(tkns_seq)

             if   "係助詞" in anlyzd_txt[0][1]:
                  joind_tkns.append([tkns_seq, "格助詞＋係助詞形,連結＆連体,*,*"])
             else:
                  joind_tkns.append([anlyzd_txt[0][0], anlyzd_txt[0][1]])

             print(tkns_seq+"9")
             print(joind_tkns)


    return joind_tkns


#テキストの中に含まれるコンテント(＝主語と述語の組,インテントに付随する内容)を抽出する(「～とは」によって作られる文型に対応)
def extract_content_with_jp_toha(tkns):
    is_mtchs_jp_toha = [False] * len(tkns)
    sub              = ""
    prdct            = ""
    content          = ""
    tkns_idx         = 0
    jp_toha_idx      = 0
    noun_cnt         = 0
    jp_toha_mtch_cnt = 0


    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "とは" and "格助詞＋係助詞形" in tkns[tkns_idx][1]):
              is_mtchs_jp_toha[tkns_idx] = True
              jp_toha_idx = tkns_idx
          tkns_idx += 1
    else:
          tkns_idx = 0

          for mtchs_idx, mtchs_flg in enumerate(is_mtchs_jp_toha):
              if mtchs_flg == True:
                 jp_toha_idx = mtchs_idx                 
                 break

    for tkn in tkns:
        if "名詞" in tkn[1]:
           noun_cnt += 1

    for flg in is_mtchs_jp_toha:
        if mtchs_flg == True:
           jp_toha_mtch_cnt += 1

    if noun_cnt == 0:
       return "主語: 述語: (文型不一致)"

    if "名詞" not in tkns[0][1]:
        return "主語: 述語: (文型不一致)"

    if jp_toha_mtch_cnt == 0:
       return "主語: 述語: (文型不一致)"

    if jp_toha_idx == len(tkns):
       return "主語: 述語: (文型不一致)"

    while tkns_idx < jp_toha_idx:
          if "名詞" in tkns[0][1]:
             sub = tkns[0][0]
          tkns_idx += 1
    else:
          tkns_idx = 2

    while tkns_idx < len(tkns):
          prdct += tkns[tkns_idx][0]
          tkns_idx += 1

    if   (sub == "" or prdct == ""):
          content = "主語: 述語: (文型不一致)"
    else:
          content = "主語:" + sub + " " + "述語:" + prdct


    return content


#テキストの中に含まれるコンテント(＝主語と述語の組,インテントに付随する内容)を抽出する(「～と」(任意個)→「～とは」によって作られる文型に対応)
def extract_content_with_jp_to_toha(tkns):
    is_mtchs_jp_to = [False] * len(tkns)
    is_mtchs_jp_toha = [False] * len(tkns)
    sub              = ""
    prdct            = ""
    content          = ""
    tkns_idx         = 0
    jp_to_idx        = 0
    jp_toha_idx      = 0
    noun_cnt         = 0
    jp_to_mtch_cnt   = 0
    jp_toha_mtch_cnt = 0


    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "と" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_to[tkns_idx] = True
              jp_to_idx = tkns_idx
          tkns_idx += 1
    else:
          tkns_idx = 0

    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "とは" and "格助詞＋係助詞形" in tkns[tkns_idx][1]):
              is_mtchs_jp_toha[tkns_idx] = True
          tkns_idx += 1
    else:
          tkns_idx = 1

          for mtchs_idx, mtchs_flg in enumerate(is_mtchs_jp_toha):
              if mtchs_flg == True:
                 jp_toha_idx = mtchs_idx
                 break

    for tkn in tkns:
        if "名詞" in tkn[1]:
           noun_cnt += 1

    for flg in is_mtchs_jp_to:
        if mtchs_flg == True:
           jp_to_mtch_cnt += 1

    for flg in is_mtchs_jp_toha:
        if mtchs_flg == True:
           jp_toha_mtch_cnt += 1

    if noun_cnt < 2:
       return "主語: 述語: (文型不一致)"

    if "名詞" not in tkns[0][1]:
        return "主語: 述語: (文型不一致)"

    if (jp_to_mtch_cnt == 0 or \
        jp_toha_mtch_cnt == 0):
        return "主語: 述語: (文型不一致)"

    if jp_to_idx > jp_toha_idx:
       return "主語: 述語: (文型不一致)"

    if jp_toha_idx == len(tkns)-1:
       return "主語: 述語: (文型不一致)"

    while tkns_idx < jp_toha_idx:
          if (tkns[tkns_idx][0] == "と" and "助詞" in tkns[tkns_idx][1]):
              if "名詞" in tkns[tkns_idx-1][1]:
                 if   sub == "":
                      sub = tkns[tkns_idx-1][0]
                 else:
                      sub = sub  + "," + tkns[tkns_idx-1][0]

          tkns_idx += 1

    else:
          if (tkns[tkns_idx][0] == "とは" and "格助詞＋係助詞形" in tkns[tkns_idx][1]):
              if "名詞" in tkns[tkns_idx-1][1]:
                 if   sub == "":
                      sub = tkns[tkns_idx-1][0]
                 else:
                      sub = sub  + "," + tkns[tkns_idx-1][0]

          tkns_idx += 1

    while tkns_idx < len(tkns):
          prdct += tkns[tkns_idx][0]
          tkns_idx += 1

    if   (sub == "" or prdct == ""):
          content = "主語: 述語: (文型不一致)"
    else:
          content = "主語:" + sub + " " + "述語:" + prdct


    return content


#テキストの中に含まれるコンテント(＝主語と述語の組,インテントに付随する内容)を抽出する(「～と」(任意個)→「～は」によって作られる文型に対応)
def extract_content_with_jp_to_ha(tkns):
    is_mtchs_jp_to = [False] * len(tkns)
    is_mtchs_jp_ha = [False] * len(tkns)
    sub            = ""
    prdct          = ""
    content        = ""
    tkns_idx       = 0
    jp_to_idx      = 0
    jp_ha_idx      = 0
    noun_cnt       = 0
    jp_to_mtch_cnt = 0
    jp_ha_mtch_cnt = 0


    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "と" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_to[tkns_idx] = True
              jp_to_idx = tkns_idx
          tkns_idx += 1
    else:
          tkns_idx = 0

    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "は" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_ha[tkns_idx] = True
          tkns_idx += 1
    else:
          tkns_idx = 1

          for mtchs_idx, mtchs_flg in enumerate(is_mtchs_jp_ha):
              if mtchs_flg == True:
                 jp_ha_idx = mtchs_idx
                 break

    for tkn in tkns:
        if "名詞" in tkn[1]:
           noun_cnt += 1

    for flg in is_mtchs_jp_to:
        if mtchs_flg == True:
           jp_to_mtch_cnt += 1

    for flg in is_mtchs_jp_ha:
        if mtchs_flg == True:
           jp_ha_mtch_cnt += 1

    if noun_cnt < 2:
       return "主語: 述語: (文型不一致)"

    if "名詞" not in tkns[0][1]:
        return "主語: 述語: (文型不一致)"

    if (jp_to_mtch_cnt == 0 or \
        jp_ha_mtch_cnt == 0):
        return "主語: 述語: (文型不一致)"

    if jp_to_idx > jp_ha_idx:
       return "主語: 述語: (文型不一致)"

    if jp_ha_idx == len(tkns)-1:
       return "主語: 述語: (文型不一致)"

    while tkns_idx < jp_ha_idx:
          if (tkns[tkns_idx][0] == "と" and "助詞" in tkns[tkns_idx][1]):
              if "名詞" in tkns[tkns_idx-1][1]:
                 if   sub == "":
                      sub = tkns[tkns_idx-1][0]
                 else:
                      sub = sub  + "," + tkns[tkns_idx-1][0]

          tkns_idx += 1

    else:
          if (tkns[tkns_idx][0] == "は" and "助詞" in tkns[tkns_idx][1]):
              if "名詞" in tkns[tkns_idx-1][1]:
                 if   sub == "":
                      sub = tkns[tkns_idx-1][0]
                 else:
                      sub = sub  + "," + tkns[tkns_idx-1][0]

          tkns_idx += 1

    while tkns_idx < len(tkns):
          prdct += tkns[tkns_idx][0]
          tkns_idx += 1

    if   (sub == "" or prdct == ""):
          content = "主語: 述語: (文型不一致)"
    else:
          content = "主語:" + sub + " " + "述語:" + prdct


    return content


#テキストの中に含まれるコンテント(＝主語と述語の組,インテントに付随する内容)を抽出する(「～と」(任意個)→「～が」によって作られる文型に対応)
def extract_content_with_jp_to_ga(tkns):
    is_mtchs_jp_to = [False] * len(tkns)
    is_mtchs_jp_ga = [False] * len(tkns)
    sub            = ""
    prdct          = ""
    content        = ""
    tkns_idx       = 0
    jp_to_idx      = 0
    jp_ga_idx      = 0
    noun_cnt       = 0
    jp_to_mtch_cnt = 0
    jp_ga_mtch_cnt = 0


    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "と" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_to[tkns_idx] = True
              jp_to_idx = tkns_idx
          tkns_idx += 1
    else:
          tkns_idx = 0

    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "が" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_ga[tkns_idx] = True
              jp_ga_idx = tkns_idx
          tkns_idx += 1
    else:
          tkns_idx = 1

          for mtchs_idx, mtchs_flg in enumerate(is_mtchs_jp_ga):
              if mtchs_flg == True:
                 jp_ga_idx = mtchs_idx
                 break

    for tkn in tkns:
        if "名詞" in tkn[1]:
           noun_cnt += 1

    for flg in is_mtchs_jp_to:
        if mtchs_flg == True:
           jp_to_mtch_cnt += 1

    for flg in is_mtchs_jp_ga:
        if mtchs_flg == True:
           jp_ga_mtch_cnt += 1

    if noun_cnt < 2:
       return "主語: 述語: (文型不一致)"

    if "名詞" not in tkns[0][1]:
        return "主語: 述語: (文型不一致)"

    if (jp_to_mtch_cnt == 0 or jp_ga_mtch_cnt == 0):
        return "主語: 述語: (文型不一致)"

    if jp_to_idx > jp_ga_idx:
       return "主語: 述語: (文型不一致)"

    if jp_ga_idx == len(tkns)-1:
       return "主語: 述語: (文型不一致)"

    while tkns_idx < jp_ga_idx:
          if (tkns[tkns_idx][0] == "と" and "助詞" in tkns[tkns_idx][1]):
              if "名詞" in tkns[tkns_idx-1][1]:
                 if   sub == "":
                      sub = tkns[tkns_idx-1][0]
                 else:
                      sub = sub  + "," + tkns[tkns_idx-1][0]

          tkns_idx += 1

    else:
          if (tkns[tkns_idx][0] == "が" and "助詞" in tkns[tkns_idx][1]):
              if "名詞" in tkns[tkns_idx-1][1]:
                 if   sub == "":
                      sub = tkns[tkns_idx-1][0]
                 else:
                      sub = sub  + "," + tkns[tkns_idx-1][0]

          tkns_idx += 1

    while tkns_idx < len(tkns):
          prdct += tkns[tkns_idx][0]
          tkns_idx += 1

    if   (sub == "" or prdct == ""):
          content = "主語: 述語: (文型不一致)"
    else:
          content = "主語:" + sub + " " + "述語:" + prdct


    return content


#テキストの中に含まれるコンテント(＝主語と述語の組,インテントに付随する内容)を抽出する(「～と」(任意個)→「～も」によって作られる文型に対応)
def extract_content_with_jp_to_mo(tkns):
    is_mtchs_jp_to = [False] * len(tkns)
    is_mtchs_jp_mo = [False] * len(tkns)
    sub            = ""
    prdct          = ""
    content        = ""
    tkns_idx       = 0
    jp_to_idx      = 0
    jp_mo_idx      = 0
    noun_cnt       = 0
    jp_to_mtch_cnt = 0
    jp_mo_mtch_cnt = 0


    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "と" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_to[tkns_idx] = True
              jp_to_idx = tkns_idx
          tkns_idx += 1
    else:
          tkns_idx = 0

    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "も" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_mo[tkns_idx] = True
              jp_mo_idx = tkns_idx
          tkns_idx += 1
    else:
          tkns_idx = 1

          for mtchs_idx, mtchs_flg in enumerate(is_mtchs_jp_mo):
              if mtchs_flg == True:
                 jp_mo_idx = mtchs_idx
                 break

    for tkn in tkns:
        if "名詞" in tkn[1]:
           noun_cnt += 1

    for flg in is_mtchs_jp_to:
        if mtchs_flg == True:
           jp_to_mtch_cnt += 1

    for flg in is_mtchs_jp_mo:
        if mtchs_flg == True:
           jp_mo_mtch_cnt += 1

    if noun_cnt < 2:
       return "主語: 述語: (文型不一致)"

    if "名詞" not in tkns[0][1]:
        return "主語: 述語: (文型不一致)"

    if (jp_to_mtch_cnt == 0 or jp_mo_mtch_cnt == 0):
        return "主語: 述語: (文型不一致)"

    if jp_to_idx > jp_mo_idx:
       return "主語: 述語: (文型不一致)"

    if jp_mo_idx == len(tkns)-1:
       return "主語: 述語: (文型不一致)"

    while tkns_idx < jp_mo_idx:
          if (tkns[tkns_idx][0] == "と" and "助詞" in tkns[tkns_idx][1]):
              if "名詞" in tkns[tkns_idx-1][1]:
                 if   sub == "":
                      sub = tkns[tkns_idx-1][0]
                 else:
                      sub = sub  + "," + tkns[tkns_idx-1][0]

          tkns_idx += 1

    else:
          if (tkns[tkns_idx][0] == "も" and "助詞" in tkns[tkns_idx][1]):
              if "名詞" in tkns[tkns_idx-1][1]:
                 if   sub == "":
                      sub = tkns[tkns_idx-1][0]
                 else:
                      sub = sub  + "," + tkns[tkns_idx-1][0]

          tkns_idx += 1

    while tkns_idx < len(tkns):
          prdct += tkns[tkns_idx][0]
          tkns_idx += 1

    if   (sub == "" or prdct == ""):
          content = "主語: 述語: (文型不一致)"
    else:
          content = "主語:" + sub + " " + "述語:" + prdct


    return content


#テキストの中に含まれるコンテント(＝主語と述語の組,インテントに付随する内容)を抽出する(「～や」(任意個)→「～は」によって作られる文型に対応)
def extract_content_with_jp_ya_ha(tkns):
    is_mtchs_jp_ya  = [False] * len(tkns)
    is_mtchs_jp_ha  = [False] * len(tkns)
    sub             = ""
    prdct           = ""
    content         = ""
    tkns_idx        = 0
    jp_ya_idx       = 0
    jp_ha_idx       = 0
    noun_cnt        = 0
    jp_ya_mtch_cnt  = 0
    jp_ha_mtch_cnt  = 0


    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "や" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_ya[tkns_idx] = True
              jp_ya_idx = tkns_idx
          tkns_idx += 1
    else:
          tkns_idx = 0

    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "は" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_ha[tkns_idx] = True
              jp_ha_idx = tkns_idx
          tkns_idx += 1
    else:
          tkns_idx = 1

          for mtchs_idx, mtchs_flg in enumerate(is_mtchs_jp_ha):
              if mtchs_flg == True:
                 jp_ha_idx = mtchs_idx
                 break

    for tkn in tkns:
        if "名詞" in tkn[1]:
           noun_cnt += 1

    for flg in is_mtchs_jp_ya:
        if mtchs_flg == True:
           jp_ya_mtch_cnt += 1

    for flg in is_mtchs_jp_ha:
        if mtchs_flg == True:
           jp_ha_mtch_cnt += 1

    if noun_cnt < 2:
       return "主語: 述語: (文型不一致)"

    if "名詞" not in tkns[0][1]:
        return "主語: 述語: (文型不一致)"

    if (jp_ya_mtch_cnt == 0 or jp_ha_mtch_cnt == 0):
        return "主語: 述語: (文型不一致)"

    if jp_ya_idx > jp_ha_idx:
       return "主語: 述語: (文型不一致)"

    if jp_ha_idx == len(tkns)-1:
       return "主語: 述語: (文型不一致)"

    while tkns_idx < jp_ha_idx:
          if (tkns[tkns_idx][0] == "や" and "助詞" in tkns[tkns_idx][1]):
              if "名詞" in tkns[tkns_idx-1][1]:
                 if   sub == "":
                      sub = tkns[tkns_idx-1][0]
                 else:
                      sub = sub  + "," + tkns[tkns_idx-1][0]

          tkns_idx += 1

    else:
          if (tkns[tkns_idx][0] == "は" and "助詞" in tkns[tkns_idx][1]):
              if "名詞" in tkns[tkns_idx-1][1]:
                 if   sub == "":
                      sub = tkns[tkns_idx-1][0]
                 else:
                      sub = sub  + "," + tkns[tkns_idx-1][0]

          tkns_idx += 1

    while tkns_idx < len(tkns):
          prdct += tkns[tkns_idx][0]
          tkns_idx += 1

    if   (sub == "" or prdct == ""):
          content = "主語: 述語: (文型不一致)"
    else:
          content = "主語:" + sub + " " + "述語:" + prdct


    return content


#テキストの中に含まれるコンテント(＝主語と述語の組,インテントに付随する内容)を抽出する(「～や」(任意個)→「～が」によって作られる文型に対応)
def extract_content_with_jp_ya_ga(tkns):
    is_mtchs_jp_ya = [False] * len(tkns)
    is_mtchs_jp_ga = [False] * len(tkns)
    sub            = ""
    prdct          = ""
    content        = ""
    tkns_idx       = 0
    jp_ya_idx      = 0
    jp_ga_idx      = 0
    noun_cnt       = 0
    jp_ya_mtch_cnt = 0
    jp_ga_mtch_cnt = 0


    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "や" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_ya[tkns_idx] = True
              jp_ya_idx = tkns_idx
          tkns_idx += 1
    else:
          tkns_idx = 0

    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "が" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_ga[tkns_idx] = True
              jp_ga_idx = tkns_idx
          tkns_idx += 1
    else:
          tkns_idx = 1

          for mtchs_idx, mtchs_flg in enumerate(is_mtchs_jp_ga):
              if mtchs_flg == True:
                 jp_ga_idx = mtchs_idx
                 break

    for tkn in tkns:
        if "名詞" in tkn[1]:
           noun_cnt += 1

    for flg in is_mtchs_jp_ya:
        if mtchs_flg == True:
           jp_ya_mtch_cnt += 1

    for flg in is_mtchs_jp_ga:
        if mtchs_flg == True:
           jp_ga_mtch_cnt += 1

    if noun_cnt < 2:
       return "主語: 述語: (文型不一致)"

    if "名詞" not in tkns[0][1]:
        return "主語: 述語: (文型不一致)"

    if (jp_ya_mtch_cnt == 0 or jp_ga_mtch_cnt == 0):
        return "主語: 述語: (文型不一致)"

    if jp_ya_idx > jp_ga_idx:
        return "主語: 述語: (文型不一致)"

    if jp_ga_idx == len(tkns)-1:
        return "主語: 述語: (文型不一致)"

    while tkns_idx < jp_ga_idx:
          if (tkns[tkns_idx][0] == "や" and "助詞" in tkns[tkns_idx][1]):
              if "名詞" in tkns[tkns_idx-1][1]:
                 if   sub == "":
                      sub = tkns[tkns_idx-1][0]
                 else:
                      sub = sub  + "," + tkns[tkns_idx-1][0]

          tkns_idx += 1

    else:
          if (tkns[tkns_idx][0] == "が" and "助詞" in tkns[tkns_idx][1]):
              if "名詞" in tkns[tkns_idx-1][1]:
                 if   sub == "":
                      sub = tkns[tkns_idx-1][0]
                 else:
                      sub = sub  + "," + tkns[tkns_idx-1][0]

          tkns_idx += 1

    while tkns_idx < len(tkns):
          prdct += tkns[tkns_idx][0]
          tkns_idx += 1

    if   (sub == "" or prdct == ""):
          content = "主語: 述語: (文型不一致)"
    else:
          content = "主語:" + sub + " " + "述語:" + prdct


    return content


#テキストの中に含まれるコンテント(＝主語と述語の組,インテントに付随する内容)を抽出する(「～や」(任意個)→「～も」によって作られる文型に対応)
def extract_content_with_jp_ya_mo(tkns):
    is_mtchs_jp_ya = [False] * len(tkns)
    is_mtchs_jp_mo = [False] * len(tkns)
    sub            = ""
    prdct          = ""
    content        = ""
    tkns_idx       = 0
    jp_ya_idx      = 0
    jp_mo_idx      = 0
    noun_cnt       = 0
    jp_ya_mtch_cnt = 0
    jp_mo_mtch_cnt = 0


    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "や" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_ya[tkns_idx] = True
              jp_ya_idx = tkns_idx
          tkns_idx += 1
    else:
          tkns_idx = 0

    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "も" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_mo[tkns_idx] = True
              jp_mo_idx = tkns_idx
          tkns_idx += 1
    else:
          tkns_idx = 1

          for mtchs_idx, mtchs_flg in enumerate(is_mtchs_jp_mo):
              if mtchs_flg == True:
                 jp_mo_idx = mtchs_idx
                 break

    for tkn in tkns:
        if "名詞" in tkn[1]:
           noun_cnt += 1

    for flg in is_mtchs_jp_ya:
        if mtchs_flg == True:
           jp_ya_mtch_cnt += 1

    for flg in is_mtchs_jp_mo:
        if mtchs_flg == True:
           jp_mo_mtch_cnt += 1

    if noun_cnt < 2:
       return "主語: 述語: (文型不一致)"

    if "名詞" not in tkns[0][1]:
        return "主語: 述語: (文型不一致)"

    if (jp_ya_mtch_cnt == 0 or jp_mo_mtch_cnt == 0):
        return "主語: 述語: (文型不一致)"

    if jp_ya_idx > jp_mo_idx:
        return "主語: 述語: (文型不一致)"

    if jp_mo_idx == len(tkns)-1:
        return "主語: 述語: (文型不一致)"

    while tkns_idx < jp_mo_idx:
          if (tkns[tkns_idx][0] == "や" and "助詞" in tkns[tkns_idx][1]):
              if "名詞" in tkns[tkns_idx-1][1]:
                 if   sub == "":
                      sub = tkns[tkns_idx-1][0]
                 else:
                      sub = sub  + "," + tkns[tkns_idx-1][0]

          tkns_idx += 1

    else:
          if (tkns[tkns_idx][0] == "も" and "助詞" in tkns[tkns_idx][1]):
              if "名詞" in tkns[tkns_idx-1][1]:
                 if   sub == "":
                      sub = tkns[tkns_idx-1][0]
                 else:
                      sub = sub  + "," + tkns[tkns_idx-1][0]

          tkns_idx += 1

    while tkns_idx < len(tkns):
          prdct += tkns[tkns_idx][0]
          tkns_idx += 1

    if   (sub == "" or prdct == ""):
          content = "主語: 述語: (文型不一致)"
    else:
          content = "主語:" + sub + " " + "述語:" + prdct


    return content


#テキストの中に含まれるコンテント(＝主語と述語の組,インテントに付随する内容)を抽出する(「～は」によって作られる文型に対応)
def extract_content_with_jp_ha(tkns):
    is_mtchs_jp_ha = [False] * len(tkns)
    sub            = ""
    prdct          = ""
    content        = ""
    tkns_idx       = 0
    jp_ha_idx      = 0
    jp_ha_mtch_cnt = 0


    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "は" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_ha[tkns_idx] = True
          tkns_idx += 1
    else:
          tkns_idx = 0

          for mtchs_idx, mtchs_flg in enumerate(is_mtchs_jp_ha):
              if mtchs_flg == True:
                 jp_ha_idx = mtchs_idx
                 break

    for flg in is_mtchs_jp_ha:
        if mtchs_flg == True:
           jp_ha_mtch_cnt += 1

    if len(tkns) < 3:
       return "主語: 述語: (文型不一致)"

    if "名詞" not in tkns[0][1]:
        return "主語: 述語: (文型不一致)"

    if jp_ha_mtch_cnt == 0:
       return "主語: 述語: (文型不一致)"

    if jp_ha_idx == len(tkns)-1:
       return "主語: 述語: (文型不一致)"

    while tkns_idx < jp_ha_idx:
          if "名詞" in tkns[tkns_idx][1]:
             sub = tkns[tkns_idx][0]
          tkns_idx += 1
    else:
          tkns_idx += 1

    while tkns_idx < len(tkns):
          prdct += tkns[tkns_idx][0]
          tkns_idx += 1

    if   (sub == "" or prdct == ""):
          content = "主語: 述語: (文型不一致)"
    else:
          content = "主語:" + sub + " " + "述語:" + prdct


    return content


#テキストの中に含まれるコンテント(＝主語と述語の組,インテントに付随する内容)を抽出する(「～が」によって作られる文型に対応)
def extract_content_with_jp_ga(tkns):
    is_mtchs_jp_ga = [False] * len(tkns)
    sub            = ""
    prdct          = ""
    content        = ""
    tkns_idx       = 0
    jp_ga_idx      = 0
    jp_ga_mtch_cnt = 0


    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "が" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_ga[tkns_idx] = True
          tkns_idx += 1
    else:
          tkns_idx = 0

          for mtchs_idx, mtchs_flg in enumerate(is_mtchs_jp_ga):
              if mtchs_flg == True:
                 jp_ga_idx = mtchs_idx
                 break

    for flg in is_mtchs_jp_ga:
        if mtchs_flg == True:
           jp_ga_mtch_cnt += 1

    if len(tkns) < 3:
       return "主語: 述語: (文型不一致)"

    if "名詞" not in tkns[0][1]:
        return "主語: 述語: (文型不一致)"

    if jp_ga_mtch_cnt == 0:
       return "主語: 述語: (文型不一致)"

    if jp_ga_idx == len(tkns)-1:
       return "主語: 述語: (文型不一致)"

    while tkns_idx < jp_mo_idx:
          if "名詞" in tkns[tkns_idx][1]:
             sub = tkns[tkns_idx][0]
          tkns_idx += 1
    else:
          tkns_idx += 1

    while tkns_idx < len(tkns):
          prdct += tkns[tkns_idx][0]
          tkns_idx += 1

    if   (sub == "" or prdct == ""):
          content = "主語: 述語: (文型不一致)"
    else:
          content = "主語:" + sub + " " + "述語:" + prdct


    return content


#テキストの中に含まれるコンテント(＝主語と述語の組,インテントに付随する内容)を抽出する(「～も」によって作られる文型に対応)
def extract_content_with_jp_mo(tkns):
    is_mtchs_jp_mo = [False] * len(tkns)
    sub            = ""
    prdct          = ""
    content        = ""
    tkns_idx       = 0
    jp_mo_idx      = 0
    jp_mo_mtch_cnt = 0


    while tkns_idx < len(tkns):
          if (tkns[tkns_idx][0] == "も" and "助詞" in tkns[tkns_idx][1]):
              is_mtchs_jp_mo[tkns_idx] = True
          tkns_idx += 1
    else:
          tkns_idx = 0

          for mtchs_idx, mtchs_flg in enumerate(is_mtchs_jp_mo):
              if mtchs_flg == True:
                 jp_mo_idx = mtchs_idx
                 break

    for flg in is_mtchs_jp_mo:
        if mtchs_flg == True:
           jp_mo_mtch_cnt += 1

    if len(tkns) < 3:
       return "主語: 述語: (文型不一致)"

    if "名詞" not in tkns[0][1]:
        return "主語: 述語: (文型不一致)"

    if jp_mo_mtch_cnt == 0:
       return "主語: 述語: (文型不一致)"

    if jp_mo_idx == len(tkns)-1:
       return "主語: 述語: (文型不一致)"

    while tkns_idx < jp_mo_idx:
          if "名詞" in tkns[tkns_idx][1]:
             sub = tkns[tkns_idx][0]
          tkns_idx += 1
    else:
          tkns_idx += 1

    while tkns_idx < len(tkns):
          prdct += tkns[tkns_idx][0]
          tkns_idx += 1

    if   (sub == "" or prdct == ""):
          content = "主語: 述語: (文型不一致)"
    else:
          content = "主語:" + sub + " " + "述語:" + prdct


    return content


#推測＆推論をする
def inference_and_speculate(orign_txts, txt_mean, txt_tkns, txt_sntmnt, txt_djst, anlyzd_img, img_ttl, img_dscrptn):
    cntxt      = "コンテキスト:実装予定"
    tpc        = "トピック:実装予定"
    usr_info   = "ユーザー情報:実装予定"
    uttrnc_mdl = "発話モーダル:実装予定"


    return cntxt, tpc, usr_info, uttrnc_mdl


#自律学習をする
def learning(orign_txts, txt_mean, txt_tkns, txt_sntmnt, txt_djst, cntxt, tpc, usr_info, uttrnc_mdl, anlyzd_img_pth, img_ttl, img_dscrptn):
    #return lrnng_rslts   


    return "学習結果:実装予定"


#返信テキストを生成する
def generate_text(orign_txts, txt_mean, txt_tkns, txt_sntmnt, txt_djst, cntxt, tpc, usr_info, uttrnc_mdl):
    sntmnt_cnddt = ["JOY", "ANGER", "PITY", "COMFORT", "MIXED", "NEUTRAL"]
    sntmnt = random.choice(sntmnt_cnddt)


    if sntmnt == "JOY":
       gnrtd_txt_cnddt = ["お世話になってます♪", "またまた～♪"]
       gnrtd_txt = random.choice(gnrtd_txt_cnddt)

    if sntmnt == "ANGER":
       gnrtd_txt_cnddt = ["それで？", "何が言いたいの？"]
       gnrtd_txt = random.choice(gnrtd_txt_cnddt)

    if sntmnt == "PITY":
       gnrtd_txt_cnddt = ["ええと・・・", "・・・"]
       gnrtd_txt = random.choice(gnrtd_txt_cnddt)

    if sntmnt == "COMFORT":
       gnrtd_txt_cnddt = ["くつろいでね", "元気でね"]
       gnrtd_txt = random.choice(gnrtd_txt_cnddt)

    if sntmnt == "MIXED":
       gnrtd_txt_cnddt = ["どうしたらいいですか？", "オロオロ 汗"]
       gnrtd_txt = random.choice(gnrtd_txt_cnddt)

    if sntmnt == "NEUTRAL":
       gnrtd_txt_cnddt = ["どうしました？", "お元気そうで"]
       gnrtd_txt = random.choice(gnrtd_txt_cnddt)


    return gnrtd_txt


#テキストからテキスト感情を生成する
def generate_text_sentiment_from_text(txt):
    txt_sntmnt = ""


    return txt_sntmnt


#テキストからテキスト要約を生成する
def generate_text_dijest_from_text(txt):
    txt_djst = ""


    return djst


#テキストからユーザー情報を生成する
def generate_user_information_from_text(txt):
    usr_info = ""


    return usr_info


#テキストから発話モーダルを生成する
def generate_utterance_modal_from_text(txt):
    uttrnc_mdl = ""


    return mdl


#ファイルから画像データを抽出して、元の画像を復元する
def restoration_image_from_imagefile(imgfl_pth):


    return cv2.imread(imgfl_pth)


#Webフォームのデータストリームから画像データを抽出して、元の画像を復元する
def restoration_image_from_datastream(dat_strm):
    img_arry   = numpy.asarray(bytearray(dat_strm.read()), dtype=numpy.uint8)
    rstrtn_img = cv2.imdecode(img_arry, 1)


    return rstrtn_img


#指定の画像を分析する
def analyze_image(img):
    img_ttl     = "画像タイトル:実装予定"
    img_dscrptn = "画像説明:実装予定"

    anlyzd_img = draw_face_boxs(img)


    return anlyzd_img, img_ttl, img_dscrptn


#分析後の画像を基に新たな画像を生成する
def generate_image(img):


    return img


#指定の説明文を基に画像を生成する
def generate_image_by_description(dscrptn):
    gnrtd_img = []


    return gnrtd_img


#指定の画像を基に画像ファイルを生成する
def generate_image_file(img, lbl):
    dt_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    gnrtd_img_pth = IMAGE_DIRECTORY + dt_now + lbl + ".jpg"
    cv2.imwrite(gnrtd_img_pth, img)


    return gnrtd_img_pth


#指定の画像の幅と高さと総ピクセル数を取得する
def retrieve_width_hight_and_pixelcount_in_image(img):
    if img is None:
       raise ValueError("img(object-reference) is none.")


    return img.shape[1], img.shape[0], img.size


#指定の画像内の単一ピクセルを変更する
def change_pixel(img, x, y, colr):
    if img is None:
       raise ValueError("img(object-reference) is none.")

    img[x, y] = colr


#指定の画像内の単一ピクセルを取得する
def retrieve_pixel(img, x, y):
    if img is None:
       raise ValueError("img(object-reference) is none.")


    return img[x, y]


#指定の画像ファイル内の矩形範囲内の複数ピクセルを設定する
def change_pixel_by_rectangle(img, x1, y1, x2, y2, colr):
    if img is None:
       raise ValueError("img(object-reference) is none.")

    img[x1:y1, x1:y2] = colr


#指定の画像のカラー形式をBGRからRGBに変換する
def convert_imagecolor_bgr_to_rgb(img):
    if img is None:
       raise ValueError("img(object-reference) is none.")


    cnvrtd_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


    return cnvrtd_img


#指定の画像のカラー形式をRGBからBGRに変換する
def convert_imagecolor_rgb_to_bgr(img):
    if img is None:
       raise ValueError("img(object-reference) is none.")


    cnvrtd_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)


    return cnvrtd_img


#BGR形式で特定の色を抽出する関数
#色相(H):0〜180	本来は0〜360だがOpenCVでは1/2の範囲になる
#彩度(S):0〜255	値が0に近づくほど白く、255に近づくほどHの色になる
#明度(V):0〜255	値が0に近づくほど黒く、255に近づくほどHの色になる
def extract_bgr_color(img, colr_lowr, colr_uppr):
    img_msk  = cv2.inRange(img, colr_lowr, colr_uppr)
    mskd_img = cv2.bitwise_and(img, img, img_msk)


    return mskd_img


#HSV形式で特定の色を抽出する関数
#色相(H):0〜180	本来は0〜360だがOpenCVでは1/2の範囲になる
#彩度(S):0〜255	値が0に近づくほど白く、255に近づくほどHの色になる
#明度(V):0〜255	値が0に近づくほど黒く、255に近づくほどHの色になる
def extract_hsv_color(img, colr_lowr, colr_uppr):
    hsv_img  = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_msk  = cv2.inRange(hsv_img, colr_lowr, colr_uppr)
    mskd_img = cv2.bitwise_and(img, img, img_msk)


    return mskd_img


#指定の画像に対応するレイベルを取得する
def retrieve_label_corresponding_to_analyzed_image(img):
    lbl = ""


    return lbl


#指定の画像に対応するタイトル(＝表題)を取得する
def retrieve_title_corresponding_to_analyzed_image(img):
    ttl = ""


    return ttl


#指定の画像に対応する説明文を取得する
def retrieve_description_corresponding_to_analyzed_image(img):
    dscrptn = ""


    return dscrptn


#指定の画像に対応するセンチメント(＝感情)を取得する
def retrieve_sentiment_corresponding_to_analyzed_image(img):
    sntmnt = ""


    return sntmnt


#指定の２つの画像が同一であるかを検査する
def check_same_two_images(img1, img2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#指定の２つの画像の内で、幅と高さを基に画像サイズを変更する
def resize_image_by_width_and_hight(img, width, hight):
    if img is None:
       raise ValueError("img(object-reference) is none.")


    rszd_img = cv2.resize(img,(wdth, hght))


    return rszd_img


#指定の２つの画像の内で、x,y各方向の倍率を基に画像サイズを変更する
def resize_image_by_scalex_and_scaley(img, sx, sy):
    if img is None:
       raise ValueError("img(object-reference) is none.")


    rszd_img = cv2.resize(img, None, sx, sy)


    return rszd_img


#指定の２つの画像の内で、一つ目の画像サイズに合わせて二つ目の画像サイズを変更する
def resize_image_by_2nd_image(img1, img2):
    if img1 is None:
       raise ValueError("img1(object-reference) is none.")

    if img2 is None:
       raise ValueError("img2(object-reference) is none.")


    rszd_image = cv2.resize(img2, img1.shape[1::-1])


    return rszd_image


#指定の２つの画像をアルファ合成する
def alphablend_image(img1, img2, blnd_rto):
    if img1 is None:
       raise ValueError("img1(object-reference) is none.")

    if img2 is None:
       raise ValueError("img2(object-reference) is none.")


    if   blnd_rto == "5:5":
         blndd_img = cv2.addWeighted(img1, 0.5, img2, 0.5, 0)

    elif blnd_rto == "7:3":
         blndd_img = cv2.addWeighted(img1, 0.7, img2, 0.3, 0)

    elif blnd_rto == "3:7":
         blndd_img = cv2.addWeighted(img1, 0.3, img2, 0.7, 0)

    else:
         raise ValueError("Invalid blnd_rto(blend-ratio).")


    return blndd_img


#指定の画像をグレイスケール化する
def convert_image_to_grayscale(img):
    if img is None:
       raise ValueError("img(object-reference) is none.")

    cpyd_img = img.copy()


    cnvrtd_img = cv2.cvtColor(cpyd_img, cv2.COLOR_BGR2GRAY)


    return cnvrtd_img


#指定の画像を２値化(＝モノクロ化)する
def convert_image_to_binary(img):
    if img is None:
       raise ValueError("img(object-reference) is none.")

    cpyd_img = img.copy()


    cnvrtd_img1      = cv2.cvtColor(cpyd_img, cv2.COLOR_BGR2GRAY)
    ret, cnvrtd_img2 = cv2.threshold(cnvrtd_img1, 100, 255, cv2.THRESH_BINARY)


    return cnvrtd_img2


#指定の２つの画像を合成する
def composit_image(img1, img2, cmpst_typ):
    if img1 is None:
       raise ValueError("img1(object-reference) is none.")

    if img2 is None:
       raise ValueError("img2(object-reference) is none.")


    if   cmpst_typ == "logical-or":
         cmpstd_img = cv2.bitwise_or(img1, img2)

    elif cmpst_typ == "logical-and":
         cmpstd_img = cv2.bitwise_and(img1, img2)

    elif cmpst_typ == "logical-xor":
         cmpstd_img = cv2.bitwise_xor(img1, img2)

    else:
         raise ValueError("Invalid cmpst_typ(composit-type).")


    return cmpstd_img


#指定の画像の色味を反転する
def invert_imagecolor(img, invrt_typ):
    if img is None:
       raise ValueError("img(object-reference) is none.")


    if   invrt_typ == "logical-not":
         invrtd_img = cv2.bitwise_not(img)

    elif invrt_typ == "negative-and-positive":
         invrtd_img = (img * -1) + 255
         invrtd_img = numpy.clip(invrtd_img, 0, 255).astype(numpy.uint8)

    else:
         raise ValueError("Invalid invrt_typ(invert-type).")


    return invrtd_img


#指定の画像に含まれる物体の一部の輪郭(＝最外周)を抽出する
def extract_only_external_contours_from_image(img, ln_colr):
    cpyd_img = img.copy()


    cnvrtd_img1      = cv2.cvtColor(cpyd_img, cv2.COLOR_BGR2GRAY)
    ret, cnvrtd_img2 = cv2.threshold(cnvrtd_img1, 100, 255, cv2.THRESH_BINARY)
    cntrs, _         = cv2.findContours(cnvrtd_img2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    img_cntr         = cv2.drawContours(cpyd_img, cntrs, -1, ln_colr, 1)


    return img_cntr


#指定の画像に含まれる物体の全ての輪郭を抽出する
def extract_all_contours_from_image(img, ln_colr):
    cpyd_img = img.copy()


    cnvrtd_img1      = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, cnvrtd_img2 = cv2.threshold(cnvrtd_img1, 100, 255, cv2.THRESH_BINARY)
    cntrs, _         = cv2.findContours(cnvrtd_img2, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    img_cntr         = cv2.drawContours(cpyd_img, cntrs, -1, ln_colr, 1)


    return img_cntr


#指定の画像に各種フィルターを適用する
def filter_image(img, fltr_typ):
    if img is None:
       raise ValueError("img(object-reference) is none.")

    cpyd_img = img.copy()


    if   fltr_typ == "Box":
         fltrd_img = cv2.blur(cpyd_img, -1, (5, 5))

    elif fltr_typ == "Median":
         fltrd_img = cv2.medianBlur(cpyd_img, 3)

    elif fltr_typ == "Bilateral":
         fltrd_img = cv2.bilateralFilter(cpyd_img, 9, 75, 75)

    elif fltr_typ == "Gaussian":
         fltrd_img = cv2.GaussianBlur(cpyd_img, (5, 5), 0, 0)

    elif fltr_typ == "Sobel":
         fltrd_img = cv2.Sobel(cpyd_img, cv2.CV_64F, 1, 0, 3)

    elif fltr_typ == "Laplacian":
         fltrd_img = cv2.filter2D(cpyd_img, cv2.CV_64F, numpy.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]]))

    elif fltr_typ == "Envoz":
         fltrd_img = cv2.filter2D(cpyd_img, cv2.CV_64F, numpy.array([[0, -1, 0], [0, 0, 0], [0, 1, 0]]))

    elif fltr_typ == "Previt":
         fltrd_img = cv2.filter2D(cpyd_img, cv2.CV_64F, numpy.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]]))

    elif fltr_typ == "Sharpen":
         fltrd_img = cv2.filter2D(cpyd_img, -1, numpy.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]))

    else:
         fltrd_img = cpyd_img


    return fltrd_img


#指定の画像に線形化フィルターを適用する
def linearize_image(img):
    if img is None:
       raise ValueError("img(object-reference) is none.")

    cpyd_img = img.copy()


    cnvrtd_img1 = convert_image_to_grayscale(cpyd_img)
    fltrd_img1  = filter_image(cnvrtd_img1, "Sharpen")

    fltrd_img2 = cv2.filter2D(fltrd_img1, -1, numpy.array([[0, 0, 0], [0, 0, 1], [0, 0, 0]]))
    lnrzd_img  = cv2.filter2D(fltrd_img2, -1, numpy.array([[0, 0, 0], [0, 0, 0], [0, 1, 0]]))


    return lnrzd_img


#指定の画像にカートゥーン化フィルターを適用する
def cartoonize_image(img):
    if img is None:
       raise ValueError("img(object-reference) is none.")

    cpyd_img = img.copy()


    cnvrtd_img1 = convert_image_to_grayscale(cpyd_img)
    fltrd_img1  = filter_image(cnvrtd_img1, "Sharpen")

    cnvrtd_img2 = convert_image_to_binary(cpyd_img, 100)
    fltrd_img2  = filter_image(cnvrtd_img2, "Sharpen")

    cmpstd_img  = composit_image(cnvrtd_img1, cnvrtd_img2, "logical-and")
    cnvrtd_img3 = cv2.cvtColor(cmpstd_img, cv2.COLOR_GRAY2BGR)

    blndd_img   = alphablend_image(cpyd_img, cnvrtd_img3, "7:3")
    crtnzd_img  = filter_image(blndd_img, "Bilateral")


    return crtnzd_img


#指定の画像から3Dシェイプ(＝３次元形状)を取得する
def retrieve_shape3d_corresponding_to_analyzed_image(img):
    shp3d = []


    return shp3d


#指定の画像から2Dテクスチャ(＝２次元模様)を取得する
def retrieve_texture2d_corresponding_to_analyzed_image(img):
    txtr2d = []


    return txtr2d


#指定の画像から3Dテクスチャ(＝３次元模様)を取得する
def retrieve_texture3d_corresponding_to_analyzed_image(img):
    txtr3d = []


    return txtr3d


#２つの2Dモデルから2Dムーヴメント(＝２次元動態)を取得する
def retrieve_movement2d_between_two_2d_model(mdl2d1, mdl2d2):
    mvmnt2d = []


    return mvmnt2d


#２つの3Dモデルから3Dムーヴメント(＝３次元動態)を取得する
def retrieve_movement3d_between_two_3d_model(mdl3d1, mdl3d2):
    mvmnt3d = []


    return mvmnt3d


#２つの2Dモデルの形状が同じものかを検査する
def check_same_two_shape2d(shp2d1, shp2d2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#２つの3Dモデルの形状が同じものかを検査する
def check_same_two_shape3d(shp3d1, shp3d2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#２つの2Dモデルのテクスチャが同じものかを検査する
def check_same_two_texture2d(mdl2d1, mdl2d2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#２つの3Dモデルのテクスチャが同じものかを検査する
def check_same_two_texture3d(mdl3d1, mdl3d2):
    is_sm  = False
    smlrty = 0
    return is_sm, smlrty


#２つの2Dモデル(の形状＆模様)が同じものかを検査する
def check_same_two_model2d(mdl2d1, mdl2d2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#２つの3Dモデル(の形状＆模様)が同じものかを検査する
def check_same_two_model3d(mdl3d1, mdl3d2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#２つの2Dムーヴメント(＝２次元動態)が同じものかを検査する
def check_same_two_movement2d(mvmnt2d1, mvmnt2d2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#２つの3Dムーヴメント(＝３次元動態)が同じものかを検査する
def check_same_two_3d_movement(mvmnt3d1, mvmnt3d2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#２つの2Dテクスチャの中間のテクスチャ(＝２次元模様)を生成する
def generate_texture2d(txtr2d1, txtr2d2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#２つの3Dテクスチャの中間のテクスチャ(＝３次元模様)を生成する
def generate_texture3d(txtr3d1, txtr3d2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#２つの2Dシェイプの中間のシェイプ(＝２次元形状)を生成する
def generate_shape2d(shp2d1, shp2d2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#２つの3Dシェイプの中間のシェイプ(＝３次元形状)を生成する
def generate_shape3d(shp3d1, shp3d2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#２つの2Dモデルの中間のテクスチャ(＝２次元模様)を生成する
def generate_two_texture2d(mdl2d1, mdl2d2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#２つの3Dモデルの中間のテクスチャ(＝３次元模様)を生成する
def generate_two_texture3d(mdl3d1, mdl3d2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#２つの2Dモデルの中間のシェイプ(＝２次元形状)を生成する
def generate_two_model2d(mdl2d1, mdl2d2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#２つの3Dモデルの中間のシェイプ(＝３次元形状)を生成する
def generate_two_model3d(mdl3d1, mdl3d2):
    is_sm  = False
    smlrty = 0


    return is_sm, smlrty


#２つの2Dムーヴメントから中間のムーヴメント(＝２次元動態)を生成する
def generate_movement2d(mvmnt2d1, mvmnt2d2):
    mvmnt2d = []


    return mvmnt2d


#２つの3Dムーヴメントから中間のムーヴメント(＝３次元動態)を生成する
def generate_movement3d(mvmnt3d1, mvmnt3d2):
    mvmnt3d = []


    return mvmnt3d


#ムーヴメント(＝２次元動態)からノーション(＝概念)やコンセプト(＝観念)を生成する
def generate_notion_and_concept_from_movement2d(mvmnt2d):
    ntn_and_cncpt = []


    return ntn_and_cncpt


#ムーヴメント(＝３次元動態)からノーション(＝概念)やコンセプト(＝観念)を生成する
def generate_notion_and_concept_from_movement3d(mvmnt3d):
    ntn_and_cncpt = []


    return ntn_and_cncpt




#人物の顔を検出して、顔を囲った枠を描画する
def draw_face_boxs(img):

    if img is None:
       raise ValueError("img(object-reference) is none.")

    drwd_img = img.copy()

    gryd_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cscd = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    if cscd is None:
       raise IOError("can't read model.")

    hght, wdth = gryd_img.shape

    min_size = (int(hght / 10), int(wdth / 10))

    bxs = cscd.detectMultiScale(gryd_img, minSize=min_size)

    for bx in bxs:
        cv2.rectangle(drwd_img, bx, (0, 0, 255), 1, cv2.LINE_AA)


    return drwd_img

