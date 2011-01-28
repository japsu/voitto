map = function() {
	this.entries.forEach(
		function(entry) {
			emit(entry.account.number, { amount: entry.amount });
		}
	)
}

reduce = function(key, values) {
	var total = 0;
	for(var i = 0; i < values.length; ++i) {
		total += values[i].amount;
	}
	
	return { amount: total };
}

formatBalanceSheet = function(intbl, out) {
	intbl.find().forEach(
		function(row) {
			account = db.accounts.findOne({number: row._id});
			
			if(account.type == 'tulos') {
				return;
			}
			
		
			db[out].save({
				_id: account.number,
			
				account: {
					number: account.number,
					name: account.name,
				},
				amount: row.value.amount
			});
		}
	)
}

