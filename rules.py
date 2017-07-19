# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser
import phoneticSymbol
import re
import tex

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
        self.subOrSup = False
        self.needSeparate = False


    def handle_starttag(self, tag, attrs):
        self.tag = tag
        if tag == 'sub' or tag == 'sup':
            self.subOrSup = True
        else:
            self.subOrSup = False

        if tag == 'br' or tag == 'p' or tag == 'img' or tag == 'td' or tag == 'label' or tag == 'div' or tag == 'tex':
            self.fed.append(' ')


    def handle_endtag(self, tag):
        if tag == 'br' or tag == 'p' or tag == 'img' or tag == 'td' or tag == 'label' or tag == 'div' or tag == 'tex':
            self.fed.append(' ')


    def handle_entityref(self, ref):
        self.fed.append(self.unescape('&' + ref + ';'))


    def handle_data(self, d):
        # if len(self.fed) == 0:
        #     pass
        # # if re.match("[A-Za-z0-9]", d[0]):
        # #     d = ' ' + d
        # # if re.match("[A-Za-z0-9]", d[-1]):
        # #     d += ' '
        # else:
        #     last = self.fed[-1]
        #     if (re.match("[A-Za-z]", last[-1]) and re.match("[A-Za-z]", d[0]) or
        #         (re.match("[0-9]", last[-1]) and re.match("[0-9]", d[0]))) and
        #         # self.needSeparate == True:
        #         # self.subOrSup == False:
        #         d = ' ' + d
        self.fed.append(d)


    def get_data(self):
        return ''.join(self.fed)


def strip_tags(htmlData):
    s = MLStripper()
    s.feed(htmlData)
    return s.get_data()


# def strip_unvisible(htmlData):
#     if not htmlData:
#         return ''
#     cleaner = Cleaner(page_structure=False)
#     cleaner.javascript = True
#     cleaner.style = True
#     try:
#         root = html.document_fromstring(htmlData)
#         return html.tostring(cleaner.clean_html(root), encoding='utf8')
#     except:
#         return ''


def removeTags(src):
    src = strip_tags(src).strip()
    return src


def removeScriptAndStyle(src):
    regScript = r'<script[^>]*?>.*?</script>'
    regStyle = r'<style[^>]*?>.*?</style>'
    insensitiveScript = re.compile(regScript, re.IGNORECASE | re.S)
    insensitiveStyle = re.compile(regStyle, re.IGNORECASE | re.S)
    src = insensitiveScript.sub(' ', src)
    src = insensitiveStyle.sub(' ', src)
    return src


def removePlusAndMinus(src):
    regSign = r'\+|-'
    subSign = re.compile(regSign, re.S)
    src = subSign.sub(' ', src)
    return src


def removeSymbols(src):
    regSign = ur',|，'
    subSign = re.compile(regSign, re.S | re.U)
    src = subSign.sub(' ', src)
    src = re.sub(ur'\^|_|＿', '', src)
    return src


def removePhoneticSymbol(src):
    pinyinPattern = re.compile('|'.join(phoneticSymbol.phoneticSymbol.keys()))
    src = pinyinPattern.sub(lambda x: phoneticSymbol.phoneticSymbol[x.group()], src)
    return src


def processSynonym(src):
    src = src.replace(u'α', 'a')
    src = src.replace(u'β', 'b')
    src = src.replace(u'ρ', 'p')
    src = src.replace(u'ω', 'w')
    src = src.replace(u'γ', 'v')
    src = src.replace(u'ν', 'v')
    src = src.replace(u'÷', '+')
    src = src.replace(u'＋', '+')
    src = src.replace(u'＝', '=')
    src = src.replace(u'－', '-')
    src = src.replace(u'×', 'x')
    src = src.replace(u'≤', '<')
    src = src.replace(u'≥', '>')
    src = src.replace(u'＞', '>')
    src = src.replace(u'＜', '<')
    return src

def processArticleSynonym(src):
    src = src.replace(u'\'ve', ' have')
    src = src.replace(u'\'ll', ' will')
    src = src.replace(u'\'m', ' am')
    src = src.replace(u'\'s', ' is')
    return src

def removeOptionFlag(src):
    regEx = ur'\b([a-zA-Z])(．|\.)'
    subEx = re.compile(regEx, re.U)
    src = subEx.sub(r'\1 ', src)
    return src


def _processTex(m):
    texStr = m.group(1)
    regRight = re.compile(r'\\right}')
    texStr = regRight.sub(r'\\right\\}', texStr)
    regBegin = re.compile(r'\\begin{[a-z]+}({[a-z]+})?')
    texStr = regBegin.sub(r' ', texStr)
    regEnd = re.compile(r'\\end{[a-z]+}')
    texStr = regEnd.sub(r' ', texStr)
    try:
        newStr = tex.parse(texStr)
    except:
        print '[parse error]' + texStr
        newStr = texStr
    # print texStr
    return newStr


def cleanSomeSymbols(m):
    texStr = m.group(0)
    # print texStr
    texStr = re.sub('{|}', '', texStr)
    return texStr


def processTex(src):
    regEx = re.compile(ur'<tex>(.*?)</tex>', re.U)
    newSrc = regEx.sub(_processTex, src.encode('utf8'))
    regSin = re.compile(r's{in|si{n|c{os|co{s|c{tan|ct{an|cta{n|c{tg|ct{g|c{ot|co{t|t{an|ta{n|t{g|l{n|l{og|lo{g|l{im|li{m', re.IGNORECASE)
    newSrc = regSin.sub(cleanSomeSymbols, newSrc)
    # regSubAndSup = re.compile(r'}?(\^|_){?', re.IGNORECASE)
    # newSrc = regSubAndSup.sub('', newSrc)
    newSrc = re.sub(r'\\{|\\}', ' ', newSrc)
    newSrc = re.sub(r'\^|_|{|}', '', newSrc)
    try:
        newSrc = '<tex>' + newSrc.decode('utf8') + '</tex>'
    except:
        print '[decode error]' + src.encode('utf8')
        newSrc = src
    return newSrc



def stripContinuousDashes(src):
    regEx = re.compile(ur'-{3,}', re.U)
    src = regEx.sub(' ', src)
    return src


def clean(src):
    src = removeScriptAndStyle(src)
    src = processTex(src)
    src = removeTags(src).strip()
    src = removePhoneticSymbol(src)
    src = removeOptionFlag(src)
    #src = removePlusAndMinus(src)
    src = removeSymbols(src)
    src = processSynonym(src)
    src = stripContinuousDashes(src)
    return src


def cleanArticle(src):
    src = removeScriptAndStyle(src)
    src = processTex(src)
    src = removeTags(src).strip()
    src = removePhoneticSymbol(src)
    src = removeOptionFlag(src)
    #src = removePlusAndMinus(src)
    src = removeSymbols(src)
    src = processSynonym(src)
    src = processArticleSynonym(src)
    src = stripContinuousDashes(src)
    return src

if __name__ == '__main__':
    src = u'-冬一作---厂,锄隙定理与余弦<tex>\\left\\{abc\\right}</tex>定理等知识和方法解决一些';
    src = u'<tex>5.在等差数列{a_{n}}中，2（a_{1}＋a_{4}＋a_{7}）十3（a_{9}＋a_{11})=24，则此数列前13项的和S_{13}=（）\nA.Z3 B.26 C.52 D.156</tex>'
    src = u'<tex>已知\overline×(新+奥+运)=2008,其中每个汉字都代表0到9的数字,相同的汉字代表相同的数字,不同的汉字代表不同的数字,则算式(\overline{新北}+京)+\frac{1}{新}×(奥+运)=___.</tex>'
    src = u'<tex>已知\overline{1}×(新+奥+运)=2008</tex>'
    src = u'<tex>1^{2}</tex>'
    src = u'<tex>(2014\\cdot 淄博期末）已知函数f（x）=2^{x}-\\frac{1}{2^{\\left | x \\right |}} （1）若f（x）=2，求x的值；]恒成立，求实数m的取值范围. （2）若2^{t}f（2t）＋mf（t）\\geqslant 0对于t\\in [1，2</tex>'
    src = u'<div><p>下列各式计算正确的是（　　）</p><p>A. <tex>x^{2}·y^{2}=(xy)^{4}</tex>  B．<tex>\\sqrt{2}+\\sqrt{3}=\\sqrt{5}</tex>   C．<tex>(a^{2}^{3}=a^{6})</tex>    D．<tex>2a^{2}+4a^{2}=6a^{4} 若2S_{n}-na_{n}=b＋log_{a}</tex> </p></div>'
    print clean(src)
