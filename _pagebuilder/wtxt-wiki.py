# -*- coding: utf-8 -*-
#
# GPL License and Copyright Notice ============================================
#  This file is part of Wrye Mash.
#
#  Wrye Mash is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  Wrye Bolt is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Wrye Mash; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Wrye Mash copyright (C) 2005, 2006, 2007, 2008, 2009 Wrye
#
# =============================================================================
# Imports ----------------------------------------------------------------------
#--Standard
import re
import os
import sys

# ------------------------------------------------------------------------------
class Callables:
    """A singleton set of objects (typically functions or class instances) that
    can be called as functions from the command line.

    Functions are called with their arguments, while object instances are called
    with their method and then their functions. E.g.:
    * bish afunction arg1 arg2 arg3
    * bish anInstance.aMethod arg1 arg2 arg3"""

    # --Ctor
    def __init__(self):
        """Initialization."""
        self.callObjs = {}

    # --Add a callable
    def add(self, callObj, callKey=None):
        """Add a callable object.

        callObj:
            A function or class instance.
        callKey:
            Name by which the object will be accessed from the command line.
            If callKey is not defined, then callObj.__name__ is used."""
        callKey = callKey or callObj.__name__
        self.callObjs[callKey] = callObj

    # --Help
    def printHelp(self, callKey):
        """Print help for specified callKey."""
        print(help(self.callObjs[callKey]))

    # --Main
    def main(self):
        callObjs = self.callObjs
        # --Call key, tail
        # This makes no sense since if there was a dot it would be in the filename
        # callParts = string.split(sys.argv[1], '.', 1)
        callKey = sys.argv[1]
        # This makes no sense because it doesn't seem to capture what is after genHtml
        # The intent here is to use callObj.__name__ but there isn't a tail
        # callTail = (len(callParts) > 1 and callParts[1])
        # --Help request?
        if callKey == '-h':
            self.printHelp(self)
            return
        # --Not have key?
        if callKey not in callObjs:
            print("Unknown function/object: {}".format(callKey))
            return
        # --Callable
        callObj = callObjs[callKey]
        if isinstance(callObj, str):
            callObj = eval(callObj)
        # The intent here is to use callObj.__name__ but there isn't a tail
        # if callTail:
        #    callObj = eval('callObj.' + callTail)
        # --Args
        args = sys.argv[2:]
        # --Keywords?
        keywords = {}
        argDex = 0
        reKeyArg = re.compile(r'^\-(\D\w+)')
        reKeyBool = re.compile(r'^\+(\D\w+)')
        while argDex < len(args):
            arg = args[argDex]
            if reKeyArg.match(arg):
                keyword = reKeyArg.match(arg).group(1)
                value = args[argDex + 1]
                keywords[keyword] = value
                del args[argDex:argDex + 2]
            elif reKeyBool.match(arg):
                keyword = reKeyBool.match(arg).group(1)
                keywords[keyword] = 1
                del args[argDex]
            else:
                argDex = argDex + 1
        # --Apply
        callObj(*args, **keywords)


# --Callables Singleton
callables = Callables()


def mainFunction(func):
    """A function for adding functions to callables."""
    callables.add(func)
    return func


# Wrye Text ===================================================================
"""This section of the module provides a single function for converting
wtxt text files to html files.

Headings:
= XXXX >> H1 "XXX"
== XXXX >> H2 "XXX"
=== XXXX >> H3 "XXX"
==== XXXX >> H4 "XXX"
Notes:
* These must start at first character of line.
* The XXX text is compressed to form an anchor. E.g == Foo Bar gets anchored as" FooBar".
* If the line has trailing ='s, they are discarded. This is useful for making
  text version of level 1 and 2 headings more readable.

Bullet Lists:
* Level 1
  * Level 2
    * Level 3
Notes:
* These must start at first character of line.
* Recognized bullet characters are: - ! ? . + * o The dot (.) produces an invisible
  bullet, and the * produces a bullet character.

Styles:
  __Text__
  ~~Italic~~
  **BoldItalic**
Notes:
* These can be anywhere on line, and effects can continue across lines.

Links:
 [[file]] produces <a href=file>file</a>
 [[file|text]] produces <a href=file>text</a>

Contents
{{CONTENTS=NN}} Where NN is the desired depth of contents (1 for single level,
2 for two levels, etc.).
"""

htmlHead = """
---
<h1>{{ page.title }}</h1>
"""
defaultCss = """
H1 { margin-top: 0in; margin-bottom: 0in; border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: none; border-right: none; padding: 0.02in 0in; background: #c6c63c; font-family: "Arial", serif; font-size: 12pt; page-break-before: auto; page-break-after: auto }
H2 { margin-top: 0in; margin-bottom: 0in; border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: none; border-right: none; padding: 0.02in 0in; background: #e6e64c; font-family: "Arial", serif; font-size: 10pt; page-break-before: auto; page-break-after: auto }
H3 { margin-top: 0in; margin-bottom: 0in; font-family: "Arial", serif; font-size: 10pt; font-style: normal; page-break-before: auto; page-break-after: auto }
H4 { margin-top: 0in; margin-bottom: 0in; font-family: "Arial", serif; font-style: italic; page-break-before: auto; page-break-after: auto }
P { margin-top: 0.01in; margin-bottom: 0.01in; font-family: "Arial", serif; font-size: 10pt; page-break-before: auto; page-break-after: auto }
P.empty {}
P.list-1 { margin-left: 0.15in; text-indent: -0.15in }
P.list-2 { margin-left: 0.3in; text-indent: -0.15in }
P.list-3 { margin-left: 0.45in; text-indent: -0.15in }
P.list-4 { margin-left: 0.6in; text-indent: -0.15in }
P.list-5 { margin-left: 0.75in; text-indent: -0.15in }
P.list-6 { margin-left: 1.00in; text-indent: -0.15in }
PRE { border: 1px solid; background: #FDF5E6; padding: 0.5em; margin-top: 0in; margin-bottom: 0in; margin-left: 0.25in}
CODE { background-color: #FDF5E6;}
BODY { background-color: #ffffcc; }
"""

# Conversion ------------------------------------------------------------------
@mainFunction
def wtxtToHtml(srcFile, outFile=None, cssDir=''):
    """Generates an html file from a wtxt file. CssDir specifies a directory to search for css files."""
    if not outFile:
        outFile = '..\\' +  os.path.splitext(srcFile)[0] + '.html'
    if srcFile:
        if srcFile == 'index.txt':
            page_number = 1
        else:
            if '-' in srcFile:
                page_number = int(srcFile.split('-', 1)[0])
            else:
                page_number = 0
    # RegEx Independent Routines ------------------------------------
    def anchorReplace(maObject):
        temp = maObject.group(1)
        anchor = reWd.sub('', temp)
        return '<div id="{}"></div>'.format(anchor)

    def boldReplace(maObject):
        state = states['bold'] = not states['bold']
        return ('</B>', '<B>')[state]

    def italicReplace(maObject):
        state = states['italic'] = not states['italic']
        return ('</I>', '<I>')[state]

    def boldItalicReplace(maObject):
        state = states['boldItalic'] = not states['boldItalic']
        return ('</I></B>', '<B><I>')[state]

    def strip_color(text):
        if reTextColor.search(text):
            temp = reTextColor.search(text)
            text_clolor = temp.group(1)
            strip_color = temp.group(0)
            fontClass = 'class="{}"'.format(text_clolor)
            out_text = re.sub(strip_color, '', text)
        else:
            fontClass = ''
            out_text = text
        return fontClass, out_text

    # RegEx ---------------------------------------------------------
    # --Headers
    reHead = re.compile(r'(=+) *(.+)')
    reHeadGreen = re.compile(r'(#+) *(.+)')
    headFormat = '<h{} class="header{}" id="{}">{}</h{}>\n'
    headFormatGreen = '<h{} id="{}">{}</h{}>\n'
    reHeaderText = re.compile(r'(<h\d {1,3}.+?>)(.*)(<\/h\d>)')
    reHeaderID = re.compile(r'(id="(.+?)")')
    # --List
    reList = re.compile(r'( *)([-!?\.\+\*o]) (.*)')
    # --Misc. text
    reHRule = re.compile(r'^\s*-{4,}\s*$')
    reEmpty = re.compile(r'\s+$')
    reMDash = re.compile(r'--')
    rePreBegin = re.compile('<pre>', re.I)
    rePreEnd = re.compile('</pre>', re.I)
    reParagraph = re.compile('<p\s+|<p>', re.I)
    reCloseParagraph = re.compile('</p>', re.I)
    # --Bold, Italic, BoldItalic
    reBold = re.compile(r'__')
    reItalic = re.compile(r'~~')
    reBoldItalic = re.compile(r'\*\*')
    states = {'bold': False, 'italic': False, 'boldItalic': False}
    # --Links
    reLink = re.compile(r'\[\[(.+?)\]\]')
    reHttp = re.compile(r' (http:\/\/[\?=_~a-zA-Z0-9\.\/%-]+)')
    reWww = re.compile(r' (www\.[\?=_~a-zA-Z0-9\./%-]+)')
    reWd = re.compile(r'(<[^>]+>|\[[^\]]+\]|\W+)')
    rePar = re.compile(r'^([a-zA-Z\d]|\*\*|~~|__|^\.{1,}|^\*{1,}|^\"{1,})')
    reFullLink = re.compile(r'(:|#|\.[a-zA-Z0-9]{2,4}$)')
    # --TextColors
    reTextColor = re.compile(r'{{a:(.+?)}}')
    # --Tags
    reAnchorTag = re.compile('{{nav:(.+?)}}')
    reContentsTag = re.compile(r'\s*{{CONTENTS=?(\d+)}}\s*$')
    reCssTag = re.compile('\s*{{CSS:(.+?)}}\s*$')
    reTitleTag = re.compile(r'^{{PAGETITLE="(.+?)"}}')
    reComment = re.compile(r'^\/\*.+\*\/')
    reCTypeBegin = re.compile(r'^\/\*')
    reCTypeEnd = re.compile('\*\/$')
    reSpoilerBegin = re.compile(r'\[\[sb:(.*?)\]\]')
    reSpoilerEnd = re.compile(r'\[\[se:\]\]')
    reBlockquoteBegin = re.compile(r'\[\[bb:(.*?)\]\]')
    reBlockquoteBEnd = re.compile(r'\[\[be:\]\]')
    reHtmlBegin = re.compile(r'(^\<font.+?\>)|(^\<code.+?\>)|(^\<a\s{1,3}href.+?\>)|(^\<a\s{1,3}(class=".+?)?href.+?\>)|(^\<img\s{1,3}src.+?\>)|^\u00A9|^\<strong|^\<[bB]\>|(^{% include image)')
    reNavigationButtonBegin = re.compile(r'{{nbb}}')
    reNavigationButtonEnd = re.compile(r'{{nbe}}')
    # --Open files
    inFileRoot = re.sub('\.[a-zA-Z]+$', '', srcFile)
    # --Images
    reImageInline = re.compile(r'{{inline:(.+?)}}')
    reImageOnly = re.compile(r'{{image:(.+?)}}')
    reImageCaption = re.compile(r'{{image-caption:(.+?)}}')
    reImageCaptionUrl = re.compile(r'{{image-cap-url:(.+?)}}')

    def imageInline(maObject):
        image_line = maObject.group(1).strip()
        if '|' in image_line:
            (max_width, file_name, alt_text) = [chunk.strip() for chunk in image_line.split('|', 2)]
        return '{{% include image-inline.html max-width="{}" file="img/{}" alt="{}" %}}'.format(max_width, file_name, alt_text)

    def imageInclude(maObject):
        image_line = maObject.group(1).strip()
        if '|' in image_line:
            (file_name, alt_text) = [chunk.strip() for chunk in image_line.split('|', 1)]
        return '{{% include image.html file="img/{}" alt="{}" %}}'.format(file_name, alt_text)

    def imageCaption(maObject):
        image_line = maObject.group(1).strip()
        if '|' in image_line:
            (file_name, alt_text, caption) = [chunk.strip() for chunk in image_line.split('|', 2)]
        return '{{% include image-caption.html file="img/{}" alt="{}" caption="{}" %}}'.format(file_name, alt_text, caption)

    def imageCaptionUrl(maObject):
        image_line = maObject.group(1).strip()
        if '|' in image_line:
            (file_name, alt_text, caption, url, urlname) = [chunk.strip() for chunk in image_line.split('|', 4)]
        return '{{% include image-caption-url.html file="img/{}" alt="{}" caption="{}" url="{}" urlname="{}" %}}'.format(file_name, alt_text, caption, url, urlname)

    def spoilerTag(line):
        spoilerID = ''
        spoilerText = ''
        if '|' in line:
            (spoilerID, spoilerText) = [chunk.strip() for chunk in line.split('|', 1)]
        spoilerID = spoilerID.lower()
        return (spoilerID, spoilerText)

    def httpReplace(line):
        temp_text = line
        if inNavigationButtons:
            temp_line = reHttp.sub(r' <a href="\1" class="drkbtn">\1</a>', temp_text)
        else:
            temp_line = reHttp.sub(r' <a href="\1">\1</a>', temp_text)
        return temp_line

    def wwwReplace(line):
        temp_text = line
        if inNavigationButtons:
            temp_line = reWww.sub(r' <a href="http://\1" class="drkbtn">\1</a>', temp_text)
        else:
            temp_line = reWww.sub(r' <a href="http://\1">\1</a>', temp_text)
        return temp_line

    def linkReplace(maObject):
        link_object = maObject.group(1)
        if '|' in link_object:
            (address, text) = [chunk.strip() for chunk in link_object.split('|', 1)]
        else:
            address = text = link_object
        fontClass, text = strip_color(text)
        if address == '#':
            address += reWd.sub('', text)
        if inNavigationButtons:
            return '<a {} href="{}" class="drkbtn">{}</a>'.format(fontClass, address, text)
        else:
            return '<a {} href="{}">{}</a>'.format(fontClass, address, text)

    # --Defaults ----------------------------------------------------------
    level = 1
    spaces = ''
    cssFile = None
    # --Init
    outLines = []
    contents = [] # The list variable for the Table of Contents
    header_match = [] # A duplicate list of the Table of Contents with numbers
    addContents = 0 # When set to 0 headers are not added to the TOC
    inPre = False
    inComment = False
    htmlIDSet = list()
    dupeEntryCount = 1
    blockAuthor = "Unknown"
    inNavigationButtons = False
    pageTitle = 'title: Your Content'
    # --Read source file --------------------------------------------------
    ins = open(srcFile, 'r')
    for line in ins:
        # --Preformatted Text Block -----------------------------
        maPreBegin = rePreBegin.search(line)
        maPreEnd = rePreEnd.search(line)
        if (inPre and not maPreEnd) or maPreBegin:
            inPre = True
            outLines.append(line)
            continue
        if maPreEnd:
            inPre = False
            outLines.append(line)
            continue
        maTitleTag = reTitleTag.match(line)
        maCTypeBegin = reCTypeBegin.match(line)
        maCTypeEnd = reCTypeEnd.search(line)
        maComment = reComment.match(line)
        if maComment:
            continue
        if inComment or maCTypeBegin or maCTypeEnd or maComment:
            inComment = maCTypeBegin or (inComment and not maCTypeEnd)
            continue
        if maTitleTag:
            temp = reTitleTag.match(line)
            pageTitle = 'title: {}'.format(temp.group(1))
        # --Re Matches -------------------------------
        maContents = reContentsTag.match(line)
        maCss = reCssTag.match(line)
        maHead = reHead.match(line)
        maHeadgreen = reHeadGreen.match(line)
        maList = reList.match(line)
        maPar = rePar.match(line)
        maHRule = reHRule.match(line)
        maEmpty = reEmpty.match(line)
        maSpoilerBegin = reSpoilerBegin.match(line)
        maSpoilerEnd = reSpoilerEnd.match(line)
        maBlockquoteBegin = reBlockquoteBegin.match(line)
        maBlockquoteEnd = reBlockquoteBEnd.match(line)
        maNavigationButtonBegin = reNavigationButtonBegin.match(line)
        maNavigationButtonEnd = reNavigationButtonEnd.match(line)
        # --Navigation Buttons ----------------------------------
        if maNavigationButtonBegin:
            line = '<div>\n'
            inNavigationButtons = True
        if maNavigationButtonEnd:
            line = '</div>\n'
            inNavigationButtons = False
        # --Contents ----------------------------------
        if maContents:
            if maContents.group(1):
                addContents = int(maContents.group(1))
            else:
                addContents = 100
        # --CSS
        elif maCss:
            cssFile = maCss.group(1).strip()
            continue
        # --Headers
        elif maHead:
            lead, text = maHead.group(1, 2)
            text = re.sub(' *=*$', '', text.strip())
            anchor = reWd.sub('', text)
            level = len(lead)
            if not htmlIDSet.count(anchor):
                htmlIDSet.append(anchor)
            else:
                anchor += str(dupeEntryCount)
                htmlIDSet.append(anchor)
                dupeEntryCount += 1
            line = headFormat.format(level, level, anchor, text, level)
            if addContents:
                contents.append((level, anchor, text))
            # --Title?
        # --Green Header
        elif maHeadgreen:
            lead, text = maHeadgreen.group(1, 2)
            text = re.sub(' *\#*$', '', text.strip())
            anchor = reWd.sub('', text)
            level = len(lead)
            if not htmlIDSet.count(anchor):
                htmlIDSet.append(anchor)
            else:
                anchor += str(dupeEntryCount)
                htmlIDSet.append(anchor)
                dupeEntryCount += 1
            line = headFormatGreen.format(level, anchor, text, level)
            if addContents:
                contents.append((level, anchor, text))
            # --Title?
        # --List item
        elif maList:
            spaces = maList.group(1)
            bullet = maList.group(2)
            text = maList.group(3)
            if bullet == '.':
                bullet = '&nbsp;'
            elif bullet == '*':
                bullet = '&bull;'
            level = int(len(spaces) / 2 + 1)
            line = '{}<p class="list-{}">{}&nbsp; '.format(spaces, level, bullet)
            line = '{}{}</p>\n'.format(line, text)
        # --HRule
        elif maHRule:
            line = '<hr>\n'
        # --Paragraph
        elif maPar:
            line = '<p>' + line.rstrip() + '</p>\n'
        # --Empty line
        elif maEmpty:
            line = spaces + '<p class="empty">&nbsp;</p>\n'
        # --Spoiler Tag ---------------------------
        elif maSpoilerBegin:
            spoilerline = maSpoilerBegin.group(1)
            spoilerID, spoilerName = spoilerTag(spoilerline)
            firstLine = '<input type="checkbox" id="{}" />\n'.format(spoilerID)
            outLines.append(firstLine)
            secondLine = '<label for="{}">{}</label>\n'.format(spoilerID, spoilerName)
            outLines.append(secondLine)
            thirdLine = '<div class="spoiler">\n'
            outLines.append(thirdLine)
            continue
        elif maSpoilerEnd:
            line = '</div>\n'
        # --Blockquote ---------------------------
        elif maBlockquoteBegin:
            firstLine = '<section class="quote">\n'
            outLines.append(firstLine)
            author = maBlockquoteBegin.group(1)
            if len(author) < 1:
                author = blockAuthor
            authorLine = '<p class="attr">{}</p>\n'.format(author)
            outLines.append(authorLine)
            continue
        elif maBlockquoteEnd:
            line = '</section>\n'
        # --Misc. Text changes --------------------
        line = reMDash.sub('&#150', line)
        line = reMDash.sub('&#150', line)
        # --Bold/Italic subs
        line = reBold.sub(boldReplace, line)
        line = reItalic.sub(italicReplace, line)
        line = reBoldItalic.sub(boldItalicReplace, line)
        # --Wtxt Tags
        line = reAnchorTag.sub(anchorReplace, line)
        # --Images
        line = reImageInline.sub(imageInline, line)
        line = reImageOnly.sub(imageInclude, line)
        line = reImageCaption.sub(imageCaption, line)
        line = reImageCaptionUrl.sub(imageCaptionUrl, line)
        # --Hyperlinks
        line = reLink.sub(linkReplace, line)
        line = httpReplace(line)
        line = wwwReplace(line)
        # --HTML Font or Code tag first of Line ------------------
        maHtmlBegin = reHtmlBegin.match(line)
        if maHtmlBegin:
            maParagraph = reParagraph.match(line)
            maCloseParagraph = reCloseParagraph.search(line)
            if not maParagraph:
                line = '<p>' + line
            if not maCloseParagraph:
                line = re.sub(r'(\n)?$', '', line)
                line = line + '</p>\n'
        # --Save line ------------------
        if maTitleTag:
            pass
        else:
            outLines.append(line)
    ins.close()
    # --Get Css -----------------------------------------------------------
    if not cssFile:
        css = defaultCss
    else:
        cssBaseName = os.path.basename(cssFile)  # --Dir spec not allowed.
        cssSrcFile = os.path.join(os.path.dirname(srcFile), cssBaseName)
        cssDirFile = os.path.join(cssDir, cssBaseName)
        if os.path.splitext(cssBaseName)[-1].lower() != '.css':
            raise "Invalid Css file: " + cssFile
        elif os.path.exists(cssSrcFile):
            cssFile = cssSrcFile
        elif os.path.exists(cssDirFile):
            cssFile = cssDirFile
        else:
            raise 'Css file not found: ' + cssFile
        css = ''.join(open(cssFile).readlines())
        if '<' in css:
            raise "Non css tag in css file: " + cssFile
    # --Write Output ------------------------------------------------------
    out = open(outFile, 'w')
    out.write('---\nlayout: default\n{}'.format(pageTitle))
    out.write(htmlHead)
    didContents = False
    countlist = [page_number, 0, 0, 0, 0, 0, 0]
    for line in outLines:
        if reContentsTag.match(line):
            if not didContents:
                if len(contents) > 0:
                    baseLevel = min([level for (level, name, text) in contents])
                else:
                    baseLevel = 1
                previousLevel = baseLevel
                for heading in contents:
                    number = ''
                    level = heading[0] - baseLevel + 1
                    if heading[0] > previousLevel:
                        countlist[level] += 1
                        for i in range(level+1):
                            if i == 0:
                                number += str(countlist[i])
                            else:
                                number += '.' + str(countlist[i])
                    if heading[0] < previousLevel:
                        # Zero out everything not a duplicate
                        for i in range(level+1, 7):
                            countlist[i] = 0
                        countlist[level] += 1
                        for i in range(level+1):
                            if i == 0:
                                number += str(countlist[i])
                            else:
                                number += '.' + str(countlist[i])
                    if heading[0] == previousLevel:
                        countlist[level] += 1
                        for i in range(level+1):
                            if i == 0:
                                number += str(countlist[i])
                            else:
                                number += '.' + str(countlist[i])
                    if heading[0] <= addContents:
                        out.write('<p class="list-{}">&bull;&nbsp; <a href="#{}">{} {}</a></p>\n'.format(level, heading[1], number, heading[2]))
                        header_match.append((heading[1], number))
                    previousLevel = heading[0]
                didContents = True
        else:
            maIsHeader = re.search(r'<\/h\d>$', line)
            if maIsHeader:
                header_id_object = reHeaderID.search(line)
                header_id_result = header_id_object.group(2)
                for header_to_match in header_match:
                    if header_to_match[0] == header_id_result:
                        split_line = reHeaderText.split(line)
                        text_replace = '{} - {}'.format(header_to_match[1], split_line[2])
                        line = '{}{}{}\n'.format(split_line[1], text_replace, split_line[3])
                        break
            out.write(line)
    out.write('</div>\n')
    out.close()
	

@mainFunction
def genHtml(fileName, outFile=None, cssDir=''):
    """Generate html from old style etxt file or from new style wtxt file."""
    ext = os.path.splitext(fileName)[1].lower()
    if ext == '.txt':
        wtxtToHtml(fileName, outFile=None, cssDir='')
        # docsDir = r'c:\program files\bethesda softworks\morrowind\data files\docs'
        # wtxt.genHtml(fileName, cssDir=docsDir)
    else:
        raise "Unrecognized file type: " + ext

if __name__ == '__main__':
        callables.main()
