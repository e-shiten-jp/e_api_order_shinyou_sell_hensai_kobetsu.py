# -*- coding: utf-8 -*-
# Copyright (c) 2021 Tachibana Securities Co., Ltd. All rights reserved.

# 2021.07.08,   yo.
# 2022.10.25 reviced,   yo.
# Python 3.6.8 / centos7.4
# API v4r3 で動作確認
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
# 機能: ログイン、信用返済売り注文（返済建玉個別指定）、ログアウト を行ないます。
#
# 利用方法: コード後半にある「プログラム始点」以下の設定項目を自身の設定に変更してご利用ください。
#
# == ご注意: ========================================
#   本番環境にに接続した場合、実際に市場に注文が出ます。
#   市場で約定した場合取り消せません。
# ==================================================
#

import urllib3
import datetime
import json
import time



#--- 共通コード ------------------------------------------------------

# request項目を保存するクラス。配列として使う。
# 'p_no'、'p_sd_date'は格納せず、func_make_url_requestで生成する。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = work_key
        self.str_value = work_value


# 口座属性クラス
class class_def_cust_property:
    def __init__(self):
        self.sUrlRequest = ''       # request用仮想URL
        self.sUrlMaster = ''        # master用仮想URL
        self.sUrlPrice = ''         # price用仮想URL
        self.sUrlEvent = ''         # event用仮想URL
        self.sZyoutoekiKazeiC = ''  # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
        self.sSecondPassword = ''   # 22.第二パスワード  APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
        self.sJsonOfmt = ''         # 返り値の表示形式指定
        


# 機能: システム時刻を"p_sd_date"の書式の文字列で返す。
# 返値: "p_sd_date"の書式の文字列
# 引数1: システム時刻
# 備考:  "p_sd_date"の書式：YYYY.MM.DD-hh:mm:ss.sss
def func_p_sd_date(int_systime):
    str_psddate = ''
    str_psddate = str_psddate + str(int_systime.year) 
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
    str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
    str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
    return str_psddate


# JSONの値の前後にダブルクオーテーションが無い場合付ける。
def func_check_json_dquat(str_value) :
    if len(str_value) == 0 :
        str_value = '""'
        
    if not str_value[:1] == '"' :
        str_value = '"' + str_value
        
    if not str_value[-1:] == '"' :
        str_value = str_value + '"'
        
    return str_value
    
    
# 受けたテキストの１文字目と最終文字の「"」を削除
# 引数：string
# 返り値：string
def func_strip_dquot(text):
    if len(text) > 0:
        if text[0:1] == '"' :
            text = text[1:]
            
    if len(text) > 0:
        if text[-1] == '\n':
            text = text[0:-1]
        
    if len(text) > 0:
        if text[-1:] == '"':
            text = text[0:-1]
        
    return text
    


# 機能: URLエンコード文字の変換
# 引数1: 文字列
# 返値: URLエンコード文字に変換した文字列
# 
# URLに「#」「+」「/」「:」「=」などの記号を利用した場合エラーとなる場合がある。
# APIへの入力文字列（特にパスワードで記号を利用している場合）で注意が必要。
#   '#' →   '%23'
#   '+' →   '%2B'
#   '/' →   '%2F'
#   ':' →   '%3A'
#   '=' →   '%3D'
def func_replace_urlecnode( str_input ):
    str_encode = ''
    str_replace = ''
    
    for i in range(len(str_input)):
        str_char = str_input[i:i+1]

        if str_char == ' ' :
            str_replace = '%20'       #「 」 → 「%20」 半角空白
        elif str_char == '!' :
            str_replace = '%21'       #「!」 → 「%21」
        elif str_char == '"' :
            str_replace = '%22'       #「"」 → 「%22」
        elif str_char == '#' :
            str_replace = '%23'       #「#」 → 「%23」
        elif str_char == '$' :
            str_replace = '%24'       #「$」 → 「%24」
        elif str_char == '%' :
            str_replace = '%25'       #「%」 → 「%25」
        elif str_char == '&' :
            str_replace = '%26'       #「&」 → 「%26」
        elif str_char == "'" :
            str_replace = '%27'       #「'」 → 「%27」
        elif str_char == '(' :
            str_replace = '%28'       #「(」 → 「%28」
        elif str_char == ')' :
            str_replace = '%29'       #「)」 → 「%29」
        elif str_char == '*' :
            str_replace = '%2A'       #「*」 → 「%2A」
        elif str_char == '+' :
            str_replace = '%2B'       #「+」 → 「%2B」
        elif str_char == ',' :
            str_replace = '%2C'       #「,」 → 「%2C」
        elif str_char == '/' :
            str_replace = '%2F'       #「/」 → 「%2F」
        elif str_char == ':' :
            str_replace = '%3A'       #「:」 → 「%3A」
        elif str_char == ';' :
            str_replace = '%3B'       #「;」 → 「%3B」
        elif str_char == '<' :
            str_replace = '%3C'       #「<」 → 「%3C」
        elif str_char == '=' :
            str_replace = '%3D'       #「=」 → 「%3D」
        elif str_char == '>' :
            str_replace = '%3E'       #「>」 → 「%3E」
        elif str_char == '?' :
            str_replace = '%3F'       #「?」 → 「%3F」
        elif str_char == '@' :
            str_replace = '%40'       #「@」 → 「%40」
        elif str_char == '[' :
            str_replace = '%5B'       #「[」 → 「%5B」
        elif str_char == ']' :
            str_replace = '%5D'       #「]」 → 「%5D」
        elif str_char == '^' :
            str_replace = '%5E'       #「^」 → 「%5E」
        elif str_char == '`' :
            str_replace = '%60'       #「`」 → 「%60」
        elif str_char == '{' :
            str_replace = '%7B'       #「{」 → 「%7B」
        elif str_char == '|' :
            str_replace = '%7C'       #「|」 → 「%7C」
        elif str_char == '}' :
            str_replace = '%7D'       #「}」 → 「%7D」
        elif str_char == '~' :
            str_replace = '%7E'       #「~」 → 「%7E」
        else :
            str_replace = str_char

        str_encode = str_encode + str_replace
        
    return str_encode



# 機能： API問合せ文字列を作成し返す。
# 戻り値： url文字列
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第２引数： ログインは、APIのurlをセット。それ以外はログインで返された仮想url（'sUrlRequest'等）の値をセット。
# 第３引数： 要求項目のデータセット。クラスの配列として受取る。
def func_make_url_request(auth_flg, \
                          url_target, \
                          work_class_req) :
    work_key = ''
    work_value = ''

    str_url = url_target
    if auth_flg == True :
        str_url = str_url + 'auth/'
    
    str_url = str_url + '?{\n\t'
    
    for i in range(len(work_class_req)) :
        work_key = func_strip_dquot(work_class_req[i].str_key)
        if len(work_key) > 0:
            if work_key[:1] == 'a' :
                work_value = work_class_req[i].str_value
            else :
                work_value = func_check_json_dquat(work_class_req[i].str_value)

            str_url = str_url + func_check_json_dquat(work_class_req[i].str_key) \
                                + ':' + work_value \
                                + ',\n\t'
               
        
    str_url = str_url[:-3] + '\n}'
    return str_url



# 機能: API問合せ。通常のrequest,price用。
# 返値: API応答（辞書型）
# 第１引数： URL文字列。
# 備考: APIに接続し、requestの文字列を送信し、応答データを辞書型で返す。
#       master取得は専用の func_api_req_muster を利用する。
def func_api_req(str_url): 
    print('送信文字列＝')
    print(str_url)  # 送信する文字列

    # APIに接続
    http = urllib3.PoolManager()
    req = http.request('GET', str_url)
    print("req.status= ", req.status )

    # 取得したデータを、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
    bytes_reqdata = req.data
    str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")

    print('返信文字列＝')
    print(str_shiftjis)

    # JSON形式の文字列を辞書型で取り出す
    json_req = json.loads(str_shiftjis)

    return json_req



# ログイン関数
# 引数1: p_noカウンター
# 引数2: アクセスするurl（'auth/'以下は付けない）
# 引数3: ユーザーID
# 引数4: パスワード
# 引数5: 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_login(int_p_no, my_url, str_userid, str_passwd, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/46 No.1 引数名:CLMAuthLoginRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLoginRequest'
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sUserId"'
    str_value = str_userid
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sPassword"'
    str_value = str_passwd
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(True, \
                                     my_url, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/46 No.2 引数名:CLMAuthLoginAck を参照してください。

    int_p_errno = int(json_return.get('p_errno'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    int_sResultCode = int(json_return.get('sResultCode'))
    # sResultCodeは、マニュアル
    # 「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、注文入力機能引数項目仕様」
    # (api_request_if_order_vOrO.pdf)
    # の p13/42 「6.メッセージ一覧」を参照ください。

    if int_p_errno ==  0 and int_sResultCode == 0:    # ログインエラーでない場合
        # ---------------------------------------------
        # ログインでの注意点
        # 契約締結前書面が未読の場合、
        # 「int_p_errno = 0 And int_sResultCode = 0」で、
        # sUrlRequest=""、sUrlEvent="" が返されログインできない。
        # ---------------------------------------------
        if len(json_return.get('sUrlRequest')) > 0 :
            # 口座属性クラスに取得した値をセット
            class_cust_property.sZyoutoekiKazeiC = json_return.get('sZyoutoekiKazeiC')
            class_cust_property.sUrlRequest = json_return.get('sUrlRequest')        # request用仮想URL
            class_cust_property.sUrlMaster = json_return.get('sUrlMaster')          # master用仮想URL
            class_cust_property.sUrlPrice = json_return.get('sUrlPrice')            # price用仮想URL
            class_cust_property.sUrlEvent = json_return.get('sUrlEvent')            # event用仮想URL
            bool_login = True
        else :
            print('契約締結前書面が未読です。')
            print('ブラウザーで標準Webにログインして確認してください。')
    else :  # ログインに問題があった場合
        print('p_errno:', json_return.get('p_errno'))
        print('p_err:', json_return.get('p_err'))
        print('sResultCode:', json_return.get('sResultCode'))
        print('sResultText:', json_return.get('sResultText'))
        print()
        bool_login = False

    return bool_login


# ログアウト
# 引数1: p_noカウンター
# 引数2: class_cust_property（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_logout(int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/46 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLogoutRequest'  # logoutを指示。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/46 No.4 引数名:CLMAuthLogoutAck を参照してください。

    int_sResultCode = int(json_return.get('sResultCode'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    if int_sResultCode ==  0 :    # ログアウトエラーでない場合
        bool_logout = True
    else :  # ログアウトに問題があった場合
        bool_logout = False

    return bool_logout

#--- 以上 共通コード -------------------------------------------------






# 参考資料（必ず最新の資料を参照してください。）--------------------------
#マニュアル
#「立花証券・ｅ支店・ＡＰＩ（v4r2）、REQUEST I/F、機能毎引数項目仕様」
# (api_request_if_clumn_v4r2.pdf)
# p4-5/46 No.5 CLMKabuNewOrder を参照してください。
#
# 5 CLMKabuNewOrder
#  1   	sCLMID	メッセージＩＤ	char*	I/O	"CLMKabuNewOrder"
#  2   	sResultCode	結果コード	char[9]	O	業務処理．エラーコード 。0：正常、5桁数字：「結果テキスト」に対応するエラーコード 
#  3   	sResultText	結果テキスト	char[512]	O	ShiftJis  「結果コード」に対応するテキスト
#  4   	sWarningCode	警告コード	char[9]	O	業務処理．ワーニングコード。0：正常、5桁数字：「警告テキスト」に対応するワーニングコード
#  5   	sWarningText	警告テキスト	char[512]	O	ShiftJis  「警告コード」に対応するテキスト
#  6   	sOrderNumber	注文番号	char[8]	O	-
#  7   	sEigyouDay	営業日	char[8]	O	営業日（YYYYMMDD）
#  8   	sZyoutoekiKazeiC	譲渡益課税区分	char[1]	I	1：特定、3：一般、5：NISA
#  9   	sTategyokuZyoutoekiKazeiC	建玉譲渡益課税区分	char[1]	I	信用建玉における譲渡益課税区分（現引、現渡で使用）
#      					*：現引、現渡以外の取引
#      					1：特定
#      					3：一般
#      					5：NISA
# 10   	sIssueCode	銘柄コード	char[12]	I	銘柄コード（6501 等）
# 11   	sSizyouC	市場	char[2]	I	00：東証
# 12   	sBaibaiKubun	売買区分	char[1]	I	1：売、3：買、5：現渡、7：現引
# 13   	sCondition	執行条件	char[1]	I	0：指定なし、2：寄付、4：引け、6：不成
# 14   	sOrderPrice	注文値段	char[14]	I	*：指定なし
#      					0：成行
#      					上記以外は、注文値段
#      					小数点については、関連資料：「立花証券・ｅ支店・ＡＰＩ、REQUEST I/F、マスタデータ利用方法」の「２－１２． 呼値」参照
# 15   	sOrderSuryou	注文数量	char[13]	I	注文数量
# 16   	sGenkinShinyouKubun	現金信用区分	char[1]	I	0：現物
#      					2：新規(制度信用6ヶ月)
#      					4：返済(制度信用6ヶ月)
#      					6：新規(一般信用6ヶ月)
#      					8：返済(一般信用6ヶ月)
# 17   	sOrderExpireDay	注文期日	char[8]	I	0：当日、上記以外は、注文期日日(YYYYMMDD)[10営業日迄]
# 18   	sGyakusasiOrderType	逆指値注文種別	char[1]	I	0：通常
# 19   	sGyakusasiZyouken	逆指値条件	char[14]	I	0：指定なし
# 20   	sGyakusasiPrice	逆指値値段	char[14]	I	*：指定なし
# 21   	sTatebiType	建日種類	char[1]	I	*：指定なし（現物または新規） 
#      					1：個別指定
#      					2：建日順
#      					3：単価益順
#      					4：単価損順
# 22   	sSecondPassword	第二パスワード	char[48]	I	第二暗証番号
#      					''：第二暗証番号省略時
#      					関連資料：「立花証券・ｅ支店・ＡＰＩ、インターフェース概要」の「３－２．ログイン、ログアウト」参照
# 23   	sOrderUkewatasiKingaku	注文受渡金額	char[16]	O	注文受渡金額
# 24   	sOrderTesuryou	注文手数料	char[16]	O	注文手数料
# 25   	sOrderSyouhizei	注文消費税	char[16]	O	注文消費税
# 26   	sKinri	金利	char[9]	O	メモリ上のシステム市場弁済別取扱条件信用新規取引の場合
#      					0～999.99999：買方金利
#      					0～999.99999：売方金利
#      					0～999.99999：買方金利（翌営業日）
#      					0～999.99999：売方金利（翌営業日）
#      					-：信用新規取引でない場合
# 27   	sOrderDate	注文日時	char[14]	O	注文日時（YYYYMMDDHHMMSS）
# 28   	aCLMKabuHensaiData	返済リスト	char[17]	I	※返済で建日種類＝個別指定の場合必須、その他は不要
#      	※必要時は以下３項目を配列とし列挙する				
#   - 1	sTategyokuNumber		char[15]	I	新規建玉番号（CLMShinyouTategyokuListのsOrderTategyokuNumber）
#   - 2	sTatebiZyuni	建日順位	char[9]	I	建日順位
#   - 3	sOrderSuryou	注文数量	char[13]	I	注文数量


#--------------------------------------
# 信用 個別返済 電文のサンプル
#
# 参考資料（必ず最新の資料を参照してください。）
#マニュアル
#「立花証券・ｅ支店・ＡＰＩ（v4r2）、REQUEST I/F、注文入力機能引数項目仕様書」
# (api_request_if_order_v4r2.pdf)
# p5/42
# "買建の売返済（制度信用×返済×個別指定×売×指値×特定口座）"
# を参照してください。
#
#
# JSON要求電文
#{
#   "sCLMID":"CLMKabuNewOrder",
#   "sZyoutoekiKazeiC":"1",
#   "sIssueCode":"4241",
#   "sSizyouC":"00",
#   "sBaibaiKubun":"1",
#   "sCondition":"0",
#   "sOrderPrice":"920",
#   "sOrderSuryou":"200",
#   "sGenkinShinyouKubun":"4",
#   "sOrderExpireDay":"0",
#   "sGyakusasiOrderType":"0",
#   "sGyakusasiZyouken":"0",
#   "sGyakusasiPrice":"*",
#   "sTatebiType":"1",
#   "sTategyokuZyoutoekiKazeiC":"*",
#   "sSecondPassword":"",
#   "aCLMKabuHensaiData":
#   [
#       {
#           "sTategyokuNumber":"202007220000402",
#           "sTatebiZyuni":"1",
#           "sOrderSuryou":"100"
#       },
#       {
#           "sTategyokuNumber":"202007220001591",
#           "sTatebiZyuni":"2",
#           "sOrderSuryou":"100"
#       }
#   ],
#   "sJsonOfmt":"1"
#}
#
#
#--------------------------------------
# JSON応答電文
#{
#   "p_sd_date":"2020.07.29-17:20:56.057",
#   "p_rv_date":"2020.07.29-17:20:55.919",
#   "p_errno":"0",
#   "p_err":"",
#   "sCLMID":"CLMKabuNewOrder",
#   "sResultCode":"0",
#   "sResultText":"",
#   "sWarningCode":"0",
#   "sWarningText":"",
#   "sOrderNumber":"0",
#   "sEigyouDay":"20200730",
#   "sOrderUkewatasiKingaku":"-2032",
#   "sOrderTesuryou":"0",
#   "sOrderSyouhizei":"0",
#   "sKinri":"-",
#   "sOrderDate":"20200729172028",
#}

# --- 以上資料 --------------------------------------------------------




# -----------------------
# 返済建玉個別指定クラス定義
# 返済データを保存するクラス。配列として使う。
# 28   	aCLMKabuHensaiData	返済リスト
#      	※必要時は以下３項目を配列とし列挙する				
#   - 1	sTategyokuNumber    新規建玉番号（CLMShinyouTategyokuListのsOrderTategyokuNumber）
#   - 2	sTatebiZyuni	建日順位
#   - 3	sOrderSuryou	注文数量
class class_def_hensai_data:
    def __init__(self):
        self.sTategyokuNumber = ''
        self.sTatebiZyuni = ''
        self.meisai_suryou = ''

    def add_data(self,str_sTategyokuNumber, str_sTatebiZyuni, str_meisai_suryou):
        self.sTategyokuNumber = func_check_json_dquat(str_sTategyokuNumber)
        self.sTatebiZyuni = func_check_json_dquat(str_sTatebiZyuni)
        self.meisai_suryou = func_check_json_dquat(str_meisai_suryou)


# -----------------------
# 機能: 返済建玉個別指定（aCLMKabuHensaiData）のテキストを作成
# 返値： aCLMKabuHensaiDataのvalue値テキスト
# 引数1: 返済建玉個別指定クラス
# 備考: 
def func_make_aCLMKabuHensaiData(class_hensai_data):
    str_value = '\n\t[\n'
    for i in range(len(class_hensai_data)):
        if not class_hensai_data[i].sTategyokuNumber == '':
            str_value = str_value + '\t\t{\n'
            str_value = str_value + '\t\t\t"sTategyokuNumber":' + class_hensai_data[i].sTategyokuNumber + ',\n'
            str_value = str_value + '\t\t\t"sTatebiZyuni":' + class_hensai_data[i].sTatebiZyuni + ',\n'
            str_value = str_value + '\t\t\t"sOrderSuryou":' + class_hensai_data[i].meisai_suryou + '\n'
            str_value = str_value + '\t\t},\n'
    if str_value[-5:] == '\t\t},\n' :
        str_value = str_value[:-2] + '\n'
    str_value = str_value + '\t]'
    
    return str_value




# 機能: 信用返済(制度信用6ヶ月) 売り注文（返済建玉個別指定）
# 返値： 辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
# 引数1: p_no
# 引数2: 銘柄コード
# 引数3: 市場（現在、東証'00'のみ）
# 引数4: 執行条件
# 引数5: 価格
# 引数6: 株数
# 引数7: 建日種類（返済優先順位）。このコードでは、2:建日順、3:単価益順、4:単価損順 のみ指定可能
# 引数8: 口座属性クラス
# 備考: このサンプルコードでは、縦日種類 1:個別指定 は指定できない。
def func_neworder_sell_sinyou_close_kobetsu(int_p_no,
                                            str_sIssueCode,
                                            str_sSizyouC,
                                            str_sCondition,
                                            str_sOrderPrice,
                                            str_sOrderSuryou,
                                            str_aCLMKabuHensaiData,
                                            class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p4/46 No.5 引数名:CLMKabuNewOrder を参照してください。

    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    # 12.売買区分  1:売 を指定
    str_sBaibaiKubun = '1'          # 12.売買区分  1:売、3:買、5:現渡、7:現引。
    # 16.現金信用区分  2:返済(制度信用6ヶ月) を指定
    str_sGenkinShinyouKubun = '4'   # 16.現金信用区分     0:現物、
                                    #                   2:新規(制度信用6ヶ月)、
                                    #                   4:返済(制度信用6ヶ月)、
                                    #                   6:新規(一般信用6ヶ月)、
                                    #                   8:返済(一般信用6ヶ月)。

    # 21.建日種類 1:個別指定 を指定
    str_sTatebiType = '1'           # 21.建日種類   *:指定なし(現物または新規) 、
                                    #               1:個別指定、
                                    #               2:建日順、
                                    #               3:単価益順、
                                    #               4:単価損順。


    # 他のパラメーターをセット
    #str_sZyoutoekiKazeiC            # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
    str_sOrderExpireDay = '0'        # 17.注文期日  0:当日、上記以外は、注文期日日(YYYYMMDD)[10営業日迄]。
    str_sGyakusasiOrderType = '0'    # 18.逆指値注文種別  0:通常、1:逆指値、2:通常+逆指値
    str_sGyakusasiZyouken = '0'      # 19.逆指値条件  0:指定なし、条件値段(トリガー価格)
    str_sGyakusasiPrice = '*'        # 20.逆指値値段  *:指定なし、0:成行、*,0以外は逆指値値段。
    str_sTategyokuZyoutoekiKazeiC =  '*'    # 9.建玉譲渡益課税区分  信用建玉における譲渡益課税区分(現引、現渡で使用)。  *:現引、現渡以外の取引、1:特定、3:一般、5:NISA
    #str_sSecondPassword             # 22.第二パスワード    APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照     ログインの返信データで設定済み。
    

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # API request区分
    str_key = '"sCLMID"'
    str_value = 'CLMKabuNewOrder'  # 新規注文を指示。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # 現物信用区分
    str_key = '"sGenkinShinyouKubun"'    # 16.現金信用区分  0:現物、2:新規(制度信用6ヶ月)、4:返済(制度信用6ヶ月)、6:新規(一般信用6ヶ月)、8:返済(一般信用6ヶ月)。
    str_value = str_sGenkinShinyouKubun
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    
    # 注文パラメーターセット
    str_key = '"sIssueCode"'    # 銘柄コード
    str_value = str_sIssueCode
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sSizyouC"'    # 市場C
    str_value = str_sSizyouC
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sBaibaiKubun"'    # 売買区分
    str_value = str_sBaibaiKubun
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sCondition"'    # 執行条件
    str_value = str_sCondition
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sOrderPrice"'    # 注文値段
    str_value = str_sOrderPrice
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sOrderSuryou"'    # 注文数量
    str_value = str_sOrderSuryou
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sTatebiType"'    # 建日種類
    str_value = str_sTatebiType
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)


    # 固定パラメーターセット
    str_key = '"sZyoutoekiKazeiC"'  # 税口座区分
    str_value = class_cust_property.sZyoutoekiKazeiC    # 引数の口座属性クラスより取得
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sOrderExpireDay"'    # 注文期日
    str_value = str_sOrderExpireDay
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sGyakusasiOrderType"'    # 逆指値注文種別
    str_value = str_sGyakusasiOrderType
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sGyakusasiZyouken"'    # 逆指値条件
    str_value = str_sGyakusasiZyouken
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sGyakusasiPrice"'    # 逆指値値段
    str_value = str_sGyakusasiPrice
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sTategyokuZyoutoekiKazeiC"'     # 9.建玉譲渡益課税区分
    str_value = str_sTategyokuZyoutoekiKazeiC
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sSecondPassword"'    # 第二パスワード   APIでは第２暗証番号を省略できない。
    str_value = class_cust_property.sSecondPassword     # 引数の口座属性クラスより取得
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)


    str_key = '"aCLMKabuHensaiData"'
    str_value = str_aCLMKabuHensaiData
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)


    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)

    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」(api_request_if_clumn_v4.pdf)
    # p4-5/46 No.5 引数名:CLMKabuNewOrder 項目1-28 を参照してください。
    
    return json_return      # 注文のjson応答文を返す







    
    
# ======================================================================================================
# ==== プログラム始点 =================================================================================
# ======================================================================================================
# 返済の明細データ用クラスの定義
class_hensai_data = [class_def_hensai_data()]


# 必要な設定項目
# 接続先:  my_url 
# ユーザーID:   my_userid 
# パスワード:    my_passwd （ログイン時に使うパスワード）
# 第2パスワード: my_2pwd （発注時に使うパスワード）
# 銘柄コード: my_sIssueCode （実際の銘柄コードを入れてください。）
# 市場: my_sSizyouC （00:東証   現在(2021/07/01)、東証のみ可能。）
# 執行条件: my_sCondition   （0:指定なし、2:寄付、4:引け、6:不成。指し値は、0:指定なし。）
# 注文値段: my_sOrderPrice  （*:指定なし、0:成行、上記以外は、注文値段。小数点については、関連資料:「立花証券・e支店・API、REQUEST I/F、マスタデータ利用方法」の「2-12. 呼値」参照。）
# 注文数量: my_sOrderSuryou


# --- 利用時に変数を設定してください -------------------------------------------------------

# 接続先 設定 --------------
# デモ環境（新バージョンになった場合、適宜変更）
my_url = 'https://demo-kabuka.e-shiten.jp/e_api_v4r3/'

# 本番環境（新バージョンになった場合、適宜変更）
# ＊＊！！実際に市場に注文が出るので注意！！＊＊
# my_url = 'https://kabuka.e-shiten.jp/e_api_v4r3/'

# ＩＤパスワード設定 ---------
my_userid = 'MY_USERID' # 自分のuseridに書き換える
my_passwd = 'MY_PASSWD' # 自分のpasswordに書き換える
my_2pwd = 'MY_2PASSWD'  # 自分の第２passwordに書き換える


# コマンド用パラメーター -------------------    
# 信用 返済 売り 注文パラメーターセット（返済建玉個別指定）
my_code = '1234'    # 10.銘柄コード。実際の銘柄コードを入れてください。
my_shijyou = '00'   # 11.市場。  00:東証   現在(2021/07/01)、東証のみ可能。
my_shikkou = '0'    # 13.執行条件。  0:指定なし、2:寄付、4:引け、6:不成。指し値は、0:指定なし。
my_kakaku = '000'   # 14.注文値段。  *:指定なし、0:成行、上記以外は、注文値段。小数点については、関連資料:「立花証券・e支店・API、REQUEST I/F、マスタデータ利用方法」の「2-12. 呼値」参照。
my_kabusuu = '000'  # 15.注文数量。


# 明細指定（aCLMKabuHensaiData）
# 備考:
#   注文数量（my_kabusuu）と、明細の数量（my_meisai_suryou）の合計が、
#   一致している必要があります。
#
#   必要な明細分を
#   「# NoXX ---------」から
#   「# -------------」まで
#   セットでコピーして利用する。
#   No1のみリストの拡張（append）の行は不要。

# No1 ---------
my_sTatebiZyuni = '1'                     # 28- 2 sTatebiZyuni 建日順位。1,2,3と返済優先順位を付ける。
my_sTategyokuNumber = '000000000000000'   # 28- 1 sTategyokuNumber 新規建玉番号（CLMShinyouTategyokuListのsOrderTategyokuNumber）
my_meisai_suryou = '000'                  # 28- 3 sOrderSuryou 注文数量。建玉株数のうちこの優先順位に指定する株数。
# class_hensai_data.append(class_def_hensai_data())     # No1は、拡張が不要。No2以降必要。
class_hensai_data[-1].add_data(my_sTategyokuNumber, my_sTatebiZyuni, my_meisai_suryou)    # パラメーターを格納。
# -------------

# No2 ---------
my_sTatebiZyuni = '2'
my_sTategyokuNumber = '000000000000000'
my_meisai_suryou = '000'
class_hensai_data.append(class_def_hensai_data())     # No2以降、必要。
class_hensai_data[-1].add_data(my_sTategyokuNumber, my_sTatebiZyuni, my_meisai_suryou)
# -------------

### No3 ---------
##my_sTatebiZyuni = '3'
##my_sTategyokuNumber = '000000000000000'
##my_meisai_suryou = '000'
##class_hensai_data.append(class_def_hensai_data())     # No2以降、必要。
##class_hensai_data[-1].add_data(my_sTategyokuNumber, my_sTatebiZyuni, my_meisai_suryou)
### -------------




# --- 以上設定項目 -------------------------------------------------------------------------


class_cust_property = class_def_cust_property()     # 口座属性クラス

# ID、パスワード、第２パスワードのURLエンコードをチェックして変換
my_userid = func_replace_urlecnode(my_userid)
my_passwd = func_replace_urlecnode(my_passwd)
class_cust_property.sSecondPassword = func_replace_urlecnode(my_2pwd)

# 返り値の表示形式指定
class_cust_property.sJsonOfmt = '5'
# "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり
# ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定

print('-- login -----------------------------------------------------')
# 送信項目、戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
# p2/46 No.1 引数名:CLMAuthLoginRequest を参照してください。
int_p_no = 1
# ログイン処理
bool_login = func_login(int_p_no, my_url, my_userid, my_passwd,  class_cust_property)


# ログインOKの場合
if bool_login :
    
    print()
    print('-- 信用 返済売り注文（21 sTatebiType 建日種類  1：個別指定）  -------------------------------------------------------------')

    # 返済リスト（28 aCLMKabuHensaiData）の明細データのテキストを作成
    str_aCLMKabuHensaiData = func_make_aCLMKabuHensaiData(class_hensai_data)
    
    int_p_no = int_p_no + 1
    # 信用 返済 売り注文    引数：p_no、銘柄コード、市場（現在、東証'00'のみ）、執行条件、価格、株数、口座属性クラス
    dic_return = func_neworder_sell_sinyou_close_kobetsu(int_p_no,
                                                        my_sIssueCode,
                                                        my_sSizyouC,
                                                        my_sCondition,
                                                        my_sOrderPrice,
                                                        my_sOrderSuryou,
                                                        str_aCLMKabuHensaiData,
                                                        class_cust_property)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」(api_request_if_clumn_v4.pdf)
    # p4-5/46 No.5 引数名:CLMKabuNewOrder 項目1-28 を参照してください。

    print('結果コード:\t', dic_return.get('sResultCode'))
    print('結果テキスト:\t', dic_return.get('sResultText'))
    print('警告コード:\t', dic_return.get('sWarningCode'))
    print('警告テキスト:\t', dic_return.get('sWarningText'))
    print('注文番号:\t', dic_return.get('sOrderNumber'))
    print('営業日:\t', dic_return.get('sEigyouDay'))
    print('注文受渡金額:\t', dic_return.get('sOrderUkewatasiKingaku'))
    print('注文手数料:\t', dic_return.get('sOrderTesuryou'))
    print('注文消費税:\t', dic_return.get('sOrderSyouhizei'))
    print('金利:\t', dic_return.get('sKinri'))
    print('注文日時:\t', dic_return.get('sOrderDate'))
    print()    


    print()
    print('-- logout -------------------------------------------------------------')
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/46 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    int_p_no = int_p_no + 1
    bool_logout = func_logout(int_p_no, class_cust_property)
   
else :
    print('ログインに失敗しました')
