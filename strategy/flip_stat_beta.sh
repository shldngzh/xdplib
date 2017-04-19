#!/bin/bash
# flip_stat
# recognize flips and conduct stat work
# EXAMPLE: ./flip_stat_beta.sh ESM5 20150529 1000
DEF_PD=1000
usage() {
cat << EOF
usage:	$0 PROD DATE PERIOD
	Recognize price flips, store (before) flip market state into file,
	and conduct summary statistics
EOF
}
PROD=$1
DATE=$2
PD=${3:-$DEF_PD}
CT=$( /opt/local/bin/lookup-ct $PROD $DATE )
YR=$( echo $DATE | cut -c1-4 )
MO=$( echo $DATE | cut -c5-6 )
DY=$( echo $DATE | cut -c7-8 )
# call rollup-subsec to generate .PDms file
~/src/rollup_subsec_beta $PROD $DATE $PD
# generate flip record file
zcat ~/data/fe/eldo/${PD}ms/$YR/$MO/$DY/eldo.$DATE.$CT.${PD}ms.L2.txt.gz | awk ' \
BEGIN { LOG10=log(10) }
# current market state
{
bidprc=$7
bidqty=$8
offprc=$9
offqty=$10
# recognize flip
if (last_offprc || last_bidprc) {
if (bidprc >= last_offprc && bidprc!=offprc) {
	fliptag=1 # market turns bid, price up
        flipcount+=1
        }
else if (offprc <= last_bidprc && bidprc!=offprc) {
        fliptag=-1 # market turns offer, price down
        flipcount+=1
        }
else	fliptag=0 # market no moves
}
# calculate ratio
if (fliptag == 1) {
        ratio=log(last_bidqty/last_offqty)/LOG10
        # print "sr="$1, "epoch="$5, "bidprc="$7, "bidqty="$8, "offprc="$9, "offqt="$10, "last_bidprc="last_bidprc, "last_bidqty="last_bidqty, \
	# 	"last_offprc="last_offprc, "last_offqty="last_offqty, "fliptype="fliptag, "LOH="ratio
	print $1, $5, $7, $8, $9, $10, last_bidprc, last_bidqty, last_offprc, last_offqty, fliptag, ratio
	}
else if (fliptag == -1) {
        ratio=log(last_offqty/last_bidqty)/LOG10
	print $1, $5, $7, $8, $9, $10, last_bidprc, last_bidqty, last_offprc, last_offqty, fliptag, ratio
	}
else	ratio=0
# store last mkt state
last_bidprc=bidprc
last_bidqty=bidqty
last_offprc=offprc
last_offqty=offqty
# store flip recognization results into file
}' \
> ./tmp.txt
gzip tmp.txt

# STATS
zcat ./tmp.txt.gz | sort -nk12 | awk ' \
{
ratio=$12
meanold=mean
mean+=(ratio-mean)/FNR
var=(FNR-1)/FNR*var + (ratio^2+(FNR-1)*(meanold)^2-FNR*mean^2)/FNR
# min, max and median
if (ratio >= max)	max=ratio
if (ratio <= min)	min=ratio
REC[i++]=ratio
}
# RETURN
END {
if (NR%2==0) median=(REC[NR/2]+REC[NR/2+1])/2
else median=REC[(NR-1)/2]
print "FlipNum="NR, "Mean="mean, "STD="sqrt(var), "Min="min, "Median="median, "Max="max
}'

