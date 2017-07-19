# -*- coding: utf-8 -*-

import re
import ply.lex as lex
import ply.yacc as yacc


def printDebug(str):
    # print str
    pass


# Tokens
tokens = (
    'BRACE2',
    'LEFT_BRACE', 'RIGHT_BRACE',
    'LEFT_DOT', 'LEFT', 'RIGHT_DOT', 'RIGHT',
    'BEGIN_ARRAY', 'END_ARRAY',
    'BRACE1',
    'SINGLE',
    'DOUBLE_BACKSLASH',
    'TEX_OTHER',
    'OTHER',
    )


t_BRACE2    = r'\\frac|\\root|\\stackrel|\\underset'
t_BRACE1    = r'\\sqrt|\\overrightarrow|\\overline|\\underline|\\widehat'
t_SINGLE    = r'\\sum|\\underbrace|\\overbrace|\\prod|\\overleftarrow|\\sin|\\cos|\\ctan|\\tan|\\ctg|\\tg|\\cot|\\ln|\\log'

t_LEFT_BRACE     = r'(\\){'
t_RIGHT_BRACE    = r'(\\)}'
t_DOUBLE_BACKSLASH   = r'\\\\'
t_TEX_OTHER   = r'\\[a-zA-Z\^]+'
# t_OTHER   = r'\d+'

t_LEFT_DOT    = r'\\left\.'
t_LEFT        = r'\\left'
t_RIGHT_DOT   = r'\\right\.'
t_RIGHT       = r'\\right'
t_BEGIN_ARRAY = r'\\begin{[a-zA-Z]+}({[a-z]+})?'
t_END_ARRAY   = r'\\end{[a-zA-Z]+}'

t_OTHER   = r'[^{}]'

# Ignored characters
t_ignore = " \t"

literals = ['{', '}']

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    # t.lexer.skip(1)
    
# Build the lexer
lexer = lex.lex()


# Parsing rules

def p_tex(t):
    '''tex : tex tex_one
           | empty'''
    if t[1] is None: t[0] = ''
    else: t[0] = t[1] + t[2]
    printDebug('tex')
    printDebug(t[0])

def p_tex_one(t):
    '''tex_one : brace2
               | brace1
               | array
               | DOUBLE_BACKSLASH
               | '{' tex '}'
               | others'''
    if t[1] == '\\\\': t[0] = ' '
    elif t[1] == '{': t[0] = '{' + t[2] + '}'
    else: t[0] = t[1]
    printDebug('tex_one')
    printDebug(t[0])

def p_empty(t):
    'empty :'
    printDebug('empty')

def p_brace2(t):
    '''brace2 : BRACE2 '{' tex '}' '{' tex '}' '''
    if t[1] == '\\frac': 
        if re.match(r'^\s*$', t[6]) or t[6] == ' ':
            t[0] = t[3]
        else:
            t[0] = t[3] + '/' + t[6]
    elif t[1] == '\\root': t[0] = t[3] + '√' + t[6]
    elif t[1] == '\\stackrel': t[0] = t[3] + ' ' + t[6]
    elif t[1] == '\\underset': t[0] = t[3] + ' ' + t[6]
    printDebug('tex_brace2')
    printDebug(t[0])

def p_brace1(t):
    '''brace1 : BRACE1 '{' tex '}' '''
    if t[1] == '\\sqrt': t[0] = '√' + t[3]
    elif t[1] == '\\overrightarrow': t[0] = t[3]
    elif t[1] == '\\overline': t[0] = t[3]
    elif t[1] == '\\underline': t[0] = t[3]
    elif t[1] == '\\widehat': t[0] = t[3]
    printDebug('brace1')
    printDebug(t[0])

# def p_big_brace(t):
#     '''big_brace : LEFT LEFT_BRACE tex RIGHT_DOT
#                  | LEFT_DOT tex RIGHT RIGHT_BRACE '''
#     if t[1] == '\\left': t[0] = '{ ' + t[3]
#     elif t[1] == '\\left\.': t[0] = t[2] + ' }'
#     printDebug('big_brace')

def p_array(t):
    '''array : BEGIN_ARRAY tex END_ARRAY '''
    t[0] = ' ' + t[2] + ' '
    printDebug('array')

def p_other(t):
    '''others : LEFT_BRACE
              | RIGHT_BRACE
              | OTHER'''
    t[0] = t[1]
    printDebug('other')
    printDebug(t[0])

def p_other2(t):
    '''others : SINGLE
              | LEFT_DOT
              | LEFT
              | RIGHT_DOT
              | RIGHT 
              | TEX_OTHER'''
    if t[1] == '\\sin': t[0] = 'sin'
    elif t[1] == '\\cos': t[0] = 'cos'
    elif t[1] == '\\ctan': t[0] = 'ctan'
    elif t[1] == '\\tan': t[0] = 'tan'
    elif t[1] == '\\ctg': t[0] = 'ctg'
    elif t[1] == '\\tg': t[0] = 'tg'
    elif t[1] == '\\cot': t[0] = 'cot'
    elif t[1] == '\\ln': t[0] = 'ln'
    elif t[1] == '\\log': t[0] = 'log'
    elif t[1] == '\\lg': t[0] = 'lg'
    elif t[1] == '\\lim': t[0] = 'lim'
    elif t[1] == '\\alpha': t[0] = 'α'
    elif t[1] == '\\beta': t[0] = 'β'
    elif t[1] == '\\gamma': t[0] = 'γ'
    elif t[1] == '\\theta': t[0] = 'θ'
    elif t[1] == '\\epsilon': t[0] = 'ε'
    elif t[1] == '\\pi': t[0] = 'π'
    elif t[1] == '\\phi': t[0] = 'φ'
    elif t[1] == '\\omega': t[0] = 'ω'
    elif t[1] == '\\nu': t[0] = 'ν'
    elif t[1] == '\\delta': t[0] = '△'
    elif t[1] == '\\Delta': t[0] = '△'
    elif t[1] == '\\triangle': t[0] = '△'
    elif t[1] == '\\angle': t[0] = '∠'
    elif t[1] == '\\infty': t[0] = '∞'
    elif t[1] == '\\sigma': t[0] = 'Σ'
    elif t[1] == '\\int': t[0] = '∫'
    elif t[1] == '\\iint': t[0] = '∫∫'

    else: t[0] = ' '
    printDebug('other2')
    printDebug(t[0])


def p_error(t):
    print("Syntax error at ")
    raise

yacc.yacc()


def parse(str):
    if not re.match(r'^\s*$', str):
        str = re.sub(r'\\sqrt\[\]', r'\\sqrt', str)
        str = re.sub(r'\\sqrt\[(.+?)\]', r'\\root{\1}', str)
        result = yacc.parse(str)
        return result
    else:
        return ''

if __name__ == '__main__':

    # s = '\\} 1 \\}'
    s = []
    s.append('\\{1')
    s.append('\\root{1}{2}')
    s.append('\\root{1}{2} \\frac{1}{2}')
    s.append('设函数f(x)=\\left\\}\\begin{array}{ccc}{{x}^{2}}-(4a+1)x-8a+4,x\\end{array}')
    s.append('\\left\\{\\begin{array}{c}x+5(x＞1)\\\\2{x}^{2}+1(x≤1)\\end{array}\\right.')
    s.append('\\stackrel{•}{6}')
    s.append('\\frac{\\frac{1}{2}}{\\root{3}{4}}\\sqrt{5}')
    s.append('\\overline{a}')
    s.append('\\widehat{y}=2.16x+a{a}')
    s.append('\\underset{lim}{n→∞}\\frac{n{a}_{n}}{{S}_{n}}')
    s.append('\\sum^{n}_{i=1}{a}^{2}_{i}')
    s.append('9\\underbrace{9…9}_{2007个9}×5\\underbrace{5…5}_{2007个5}')
    s.append('\\overbrace{●●●}^{ }')
    s.append('\\prod^{n}_{i=1}')
    s.append('  ')
    s.append('<div><p>下列各式计算正确的是（　　）</p><p>A. <tex>x^{2}·y^{2}=(xy)^{4}</tex>  B．<tex>\\sqrt{2}+\\sqrt{3}=\\sqrt{5}</tex>   C．<tex>(a^{2}^{3}=a^{6})</tex>    D．<tex>2a^{2}+4a^{2}=6a^{4}</tex> </p></div>')
    s.append(''' "2、如图.D、E、F分别是\\Delta ABC三边的中点.
 （1〕求证：AD与EF互相平分.
 （2）若∠BAC= 90^{\\circ}，试说明四边形AEDF的形状，
   并简要说明理由.", "2、如图，D、E、F分别是\\delta ABC三边的中点.
 （1〕求证：AD与EF互相平分.
 （2）若\\angle BAC=90^{\\circ}\\int{xy}，试说明四边形AEDF的形状，
 并简要说明理由."  ''')
    s.append(''' 33.已知等差数列{a_{n}}的前n项和为S_{n}，首项为1的等比数列{b_{n}}的公比为q，S_{2}=a_{3}=a_{3}，且
a_{1}，a_{3}，b_{4}成等比数列。（1）求{a_{n}}和b_{n}的通项公式；（2）设数列
{b_{n}}的前n项和为T_{n}，若2S_{n}-na_{n}=b＋lOg_{a}（2T_{n}＋1）对一切正整数n成立，求实数a，b的值。", "33.已知等差数列{a_{n}}的前n项和为S_{n},首项为1的等比数列{b_{n}}的公比为q，S_{2}=a_{3}=b_{3}，且
a_{1}，a_{3}，b_{4}成等比数列。（1）求{a_{n}}和{b_{n}}的通项公式；（2）设数列
{b_{n}}的前n项和为T_{n}，若2S_{n}-na_{n}=b＋log_{a}（2T_{n}＋1）对一切正整数n成立，求实数a，b的值。  ''')
    s.append('\\sqrt[3]{5}')
    s.append('已知A=\\sqrt[4x-y-3]{x+2}是x+2\\sqrt[3x+2y-9]{2-y}')
    s.append(''' \\left\\{\\begin{matrix}
 3x-2>x+2& \\\\
\\frac{1}{2}x-1\\leqslant 7-\\frac{3}{2}x & 
\\end{matrix}\\right.
''')
    s.append('1.下列词语中,每对加点字的读音都相同的一组是()(3分) A.慰藉/狼藉 伫立/贮蓄 B.瞰望/捍卫 栅栏/姗姗来迟 C.赦免/显赫 告馨/温馨 D.沉湎/腼腆 诘难\\落难')

    for text in s:
        result = parse(text)
        print 'result: ' + result
