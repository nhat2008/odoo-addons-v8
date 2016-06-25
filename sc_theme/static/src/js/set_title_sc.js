openerp.sc_theme=function(instance){
	instance.web.WebClient.include({
		_title_changed: function(){
			document.title = "SONG CAU";
		}		
	});	
};