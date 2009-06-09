<?xml version="1.0"  encoding='UTF-8'?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:param name="xml" select="'../export.xml'"/>
  <xsl:key name="distinct-abbr" match="item" use="."/>

  <xsl:template match="kura-transform">
     <xsl:apply-templates select="document($xml)/interlinear-text"/>
  </xsl:template>
  
  <xsl:template match="interlinear-text">
    <HTML>
    <HEAD>
      <LINK REL="stylesheet" HREF="http://www.kura.ats.lmu.de/kura-text.css" TYPE="text/css"/>
      <TITLE>
        <xsl:value-of select="item[@type='title']"/>
      </TITLE>
    </HEAD>
    <BODY>
    <DIV ID="headline">
      <xsl:value-of select="item[@type='title']"/>
    </DIV>
    <DIV ID="description">
      <xsl:value-of select="item[@type='description']"/>
    </DIV>
    <xsl:apply-templates select="phrases"/>
    <HR/>
    <B>Abbreviations:</B><BR/>
    <DIV CLASS="abbreviations">
    <xsl:for-each select="//item[@type='ABBR'][generate-id()=generate-id(key('distinct-abbr',.))]">
      <xsl:sort select="text()"/>
      <xsl:value-of select="text()"/>&#160;<xsl:value-of select="@full"/>,&#160;
    </xsl:for-each>
    </DIV><BR/>
    <B>Functions:</B><BR/>
    <DIV CLASS="abbreviations">
    <xsl:for-each select="//item[@type='FUNC'][generate-id()=generate-id(key('distinct-abbr',.))]">
      <xsl:sort select="text()"/>
      <xsl:value-of select="text()"/>&#160;<xsl:value-of select="@full"/>,&#160;
    </xsl:for-each>
    </DIV>
    </BODY>
    </HTML>
  </xsl:template>
  
  <xsl:template match="phrases">
     <DIV ID="phrases">
     <xsl:apply-templates select="phrase"/>
     </DIV>
  </xsl:template>

  <xsl:template match="phrase">
    <DIV CLASS="phrase">
    <TABLE BORDER="0" MARGIN="0" PADDING="5">
    <TR>
    <TD VALIGN="TOP"><SPAN CLASS="number">(<xsl:value-of select="item[@type='number']"/>)</SPAN></TD>
    <TD VALIGN="TOP">
      <xsl:apply-templates select="words"/>
    </TD>
    </TR>
    <TR>
    <TD></TD>
    <TD><DIV CLASS="translation">'<xsl:value-of select="item[@type='TR']"/>'&#0160;
      <xsl:choose>
      <xsl:when test="item[@type='REF']">
        [<xsl:value-of select="item[@type='REF']"/>]
      </xsl:when>  
      <xsl:when test="item[@type='REF2']">
        [<xsl:value-of select="item[@type='REF2']"/>]
      </xsl:when>
      <xsl:otherwise>
        [no reference]
      </xsl:otherwise>
      </xsl:choose>
    </DIV></TD>
    </TR>
    <TR><TD COLSPAN="2">&#0160;</TD>
    </TR>
    </TABLE>
    </DIV>
  </xsl:template>

  <xsl:template match="words">
      <xsl:apply-templates select="word"/>
  </xsl:template>

  <xsl:template match="word">
    <SPAN CLASS="multline">
      <!--<SPAN CLASS="text"><xsl:value-of select="item[@type='text']"/></SPAN><BR/>-->
      <SPAN CLASS="ilr">
      <xsl:for-each select="morphemes/morph">
        <xsl:value-of select="item[@type='text']"/>
        <xsl:if test="position()!=last()">-</xsl:if>
      </xsl:for-each>
      </SPAN><BR/>
      <SPAN CLASS="glosse">
      <xsl:for-each select="morphemes/morph">
        <xsl:for-each select="item[@type='FUNC' or @type='ABBR' or @type='GL']">
          <xsl:choose>
          <xsl:when test="@type='GL'">
            <SPAN CLASS="glsform">
            <xsl:value-of select="."/>
            </SPAN>
            <xsl:if test="position()!=last()">:</xsl:if>
          </xsl:when>
          <xsl:when test="@type='ABBR'">
            <SPAN CLASS="glsmorph">
            <xsl:value-of select="."/>
            </SPAN>
            <xsl:if test="position()!=last()">:</xsl:if>
          </xsl:when>
          <xsl:when test="@type='FUNC'">
            <SPAN CLASS="glsmorph">
            <xsl:value-of select="."/>
            </SPAN>
            <xsl:if test="position()!=last()">:</xsl:if>
          </xsl:when>
          </xsl:choose>
        </xsl:for-each>
        <xsl:if test="position()!=last()">-</xsl:if>
      </xsl:for-each>
      </SPAN><BR/>
      <SPAN CLASS="glosse">
        <xsl:value-of select="item[@type='INDX']"/>
      </SPAN>
    </SPAN><!--<SPAN class="multiline">&#0160;</SPAN>-->
  </xsl:template>
  
</xsl:stylesheet>
