<?xml version="1.0"  encoding='UTF-8'?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="text" encoding="UTF-8"/>

  <xsl:param name="xml" select="'../export.xml'"/>
  <xsl:key name="distinct-abbr" match="item" use="."/>

  <xsl:template match="kura-transform">
     <xsl:apply-templates select="document($xml)/interlinear-text"/>
  </xsl:template>
  
  <xsl:template match="interlinear-text">
    <xsl:apply-templates select="phrases"/>
\section{Abbreviations}
    <xsl:for-each select="//item[@full!='None' and @full!='Translation'][generate-id()=generate-id(key('distinct-abbr',.))]">
      <xsl:sort select="text()"/>
<xsl:value-of select="text()"/>=<xsl:value-of select="@full"/>\newline{}
    </xsl:for-each>
  </xsl:template>
  
  <xsl:template match="phrases">
     <xsl:apply-templates select="phrase"/>
  </xsl:template>

  <xsl:template match="phrase">
\begin{exe}
\ex
<xsl:apply-templates select="words"/>
\trans \glq{}<xsl:value-of select="item[@type='TR']"/>\grq{}
\end{exe}
  <!--      <xsl:choose>
      <xsl:when test="item[@type='REF']">
        [<xsl:value-of select="item[@type='REF']"/>]
      </xsl:when>  
      <xsl:when test="item[@type='REF2']">
        [<xsl:value-of select="item[@type='REF2']"/>]
      </xsl:when>
      <xsl:otherwise>
        [no reference]
      </xsl:otherwise>
      </xsl:choose>-->
  </xsl:template>

  <xsl:template match="words">
\gll <xsl:for-each select="word"><xsl:for-each select="morphemes/morph">\emph{<xsl:value-of select="item[@type='text']"/>}<xsl:if test="position()!=last()">-</xsl:if></xsl:for-each>&#160;</xsl:for-each> \\
     <xsl:for-each select="word"><xsl:for-each select="morphemes/morph"><xsl:for-each select="item[@type='FUNC' or @type='ABBR' or @type='GL']"><xsl:choose><xsl:when test="@type='GL'"><xsl:value-of select="."/><xsl:if test="position()!=last()">:</xsl:if></xsl:when><xsl:otherwise>{\small <xsl:value-of select="."/>}<xsl:if test="position()!=last()">:</xsl:if></xsl:otherwise></xsl:choose></xsl:for-each><xsl:if test="position()!=last()">-</xsl:if></xsl:for-each>&#160;</xsl:for-each> \\
      <!--<xsl:apply-templates select="word"/>-->
  </xsl:template>

  <xsl:template match="word">
      <!--<SPAN CLASS="text"><xsl:value-of select="item[@type='text']"/></SPAN><BR/>-->
      <xsl:for-each select="morphemes/morph">
        <xsl:value-of select="item[@type='text']"/>
        <xsl:if test="position()!=last()">-</xsl:if>
      </xsl:for-each>} \\
      
      <xsl:for-each select="morphemes/morph">
        <xsl:for-each select="item[@type='FUNC' or @type='ABBR' or @type='GL']">
          <xsl:choose>
          <xsl:when test="@type='GL'">
            <xsl:value-of select="."/>
            <xsl:if test="position()!=last()">:</xsl:if>
          </xsl:when>
          <xsl:when test="@type='ABBR'">
            <xsl:value-of select="."/>
            <xsl:if test="position()!=last()">:</xsl:if>
          </xsl:when>
          <xsl:when test="@type='FUNC'">
            <xsl:value-of select="."/>
            <xsl:if test="position()!=last()">:</xsl:if>
          </xsl:when>
          </xsl:choose>
        </xsl:for-each>
        <xsl:if test="position()!=last()">-</xsl:if>
      </xsl:for-each>

      <xsl:value-of select="item[@type='INDX']"/>
  </xsl:template>
  
</xsl:stylesheet>