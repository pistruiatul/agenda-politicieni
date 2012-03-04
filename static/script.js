$(function() {
	// $('.person-filter select').change(function() {
	//     $(this).parents('form').submit();
	// });

	$senator = $('.office-senator');
	$deputy  = $('.office-deputy');

	$('.person-filter select').change(function(){
		var val = $(this).val();
		if(val == 'deputy')
			showDeputy();
		if(val == 'senator')
			showSenator();
		if(val == '') {
			$senator.removeClass('hide-person hidden-person');
			$deputy.removeClass('hide-person hidden-person');
		}
	});

	var showSenator = function() {
		$senator.removeClass('hide-person hidden-person');
		$deputy.addClass('hide-person');
		setTimeout(function(){
			$deputy.addClass('hidden-person');
		}, 1000);
	}

	var showDeputy = function() {
		$deputy.removeClass('hide-person hidden-person');
		$senator.addClass('hide-person');
		setTimeout(function(){
			$senator.addClass('hidden-person');
		}, 1000);
	}
});
