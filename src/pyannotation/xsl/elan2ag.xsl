<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" xmlns="http://www.w3.org/1999/xhtml" xmlns:xlink="http://www.w3.org/1999/xlink">
<xsl:output encoding="utf-8" />

<xsl:template match="ANNOTATION_DOCUMENT">
	<AGSet id="from_elan" version="1.0"  xmlns="http://www.ldc.upenn.edu/atlas/ag/" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dc="http://purl.org/DC/documents/rec-dces-19990702.htm">

		<xsl:apply-templates select="HEADER"/>
		<AG id="from_elan:AG1" type="type" timeline="from_elan:Timeline1">
		<Metadata>
		<xsl:for-each select="TIER">
		<xsl:element name="{@TIER_ID}.ElanTier.DefaultLocale"><xsl:value-of select="@DEFAULT_LOCALE" /></xsl:element>
        <xsl:if test="@PARENT_REF">
			<xsl:element name="{@TIER_ID}.ElanTier.Parent"><xsl:value-of select="@PARENT_REF" /></xsl:element>
        </xsl:if>
        </xsl:for-each>
        </Metadata>
		<xsl:apply-templates select="TIME_ORDER"/>
		<xsl:apply-templates select="TIER"/>
		<!--<xsl:apply-templates select="CONTROLLED_VOCABULARY"/>-->
        </AG>

	</AGSet>
</xsl:template>

<xsl:template match="HEADER">
<Timeline id="from_elan:Timeline1">
	<xsl:for-each select="MEDIA_DESCRIPTOR">
		<Signal id="from_elan:Timeline1:Signal{position()}" mimeClass="{@MIME_TYPE}" mimeType="{@MIME_TYPE}" encoding="not determined" xlink:type="simple" xlink:href="{@MEDIA_URL}" unit="{../@TIME_UNITS}"/>
	</xsl:for-each>
</Timeline>
</xsl:template>

<xsl:template match="TIME_ORDER">
	<xsl:for-each select="TIME_SLOT">
		<Anchor id="from_elan:AG1:{@TIME_SLOT_ID}" offset="{@TIME_VALUE}" unit="{../../HEADER/@TIME_UNITS}" signals="" />
	</xsl:for-each>    
</xsl:template>

<xsl:template match="TIER">
	<xsl:for-each select="ANNOTATION">
		<xsl:apply-templates select="ALIGNABLE_ANNOTATION">
			<xsl:with-param name="tier_type" select="../@LINGUISTIC_TYPE_REF" />
			<xsl:with-param name="tier_id" select="../@TIER_ID" />
		</xsl:apply-templates>
		<xsl:apply-templates select="REF_ANNOTATION">
			<xsl:with-param name="tier_type" select="../@LINGUISTIC_TYPE_REF" />
			<xsl:with-param name="tier_id" select="../@TIER_ID" />
		</xsl:apply-templates>
	</xsl:for-each>
</xsl:template>

<xsl:template match="REF_ANNOTATION">
	<xsl:param name="tier_id" />
	<xsl:param name="tier_type" />
	<xsl:variable name="annotation_ref" select="@ANNOTATION_REF" />

	<Annotation id="from_elan:AG1:{@ANNOTATION_ID}" type="{$tier_type}" startAnchor="from_elan:AG1:{//ALIGNABLE_ANNOTATION[@ANNOTATION_ID=$annotation_ref]/@TIME_SLOT_REF1}" endAnchor="from_elan:AG1:{//ALIGNABLE_ANNOTATION[@ANNOTATION_ID=$annotation_ref]/@TIME_SLOT_REF2}">
		<Feature name="description"><xsl:value-of select="ANNOTATION_VALUE[text()]" /></Feature>
		<Feature name="tier"><xsl:value-of select="$tier_id" /></Feature>
	</Annotation>
</xsl:template>

<xsl:template match="ALIGNABLE_ANNOTATION">
	<xsl:param name="tier_id" />
	<xsl:param name="tier_type" />

	<Annotation id="from_elan:AG1:{@ANNOTATION_ID}" type="{$tier_type}" startAnchor="from_elan:AG1:{@TIME_SLOT_REF1}" endAnchor="from_elan:AG1:{@TIME_SLOT_REF2}">
		<Feature name="description"><xsl:value-of select="ANNOTATION_VALUE[text()]" /></Feature>
		<Feature name="tier"><xsl:value-of select="$tier_id" /></Feature>
	</Annotation>
</xsl:template>

</xsl:stylesheet>

