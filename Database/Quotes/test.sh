#!\bin\bash
for i in `seq 1 1000`;
do
	wget -q -O quotes http://www.quotedb.com/quote/quote.php?action=random_quote;
	cat quotes>>final.txt;
done
