from IPython.display import HTML

def hide_code():
	return HTML('''<script>
	code_show=true; 
	function code_toggle() {
	 if (code_show){
	 $("div.input").hide();
	 } else {
	 $("div.input").show();
	 }
	 code_show = !code_show
	} 
	$( document ).ready(code_toggle);
	</script>
	The raw code for this IPython notebook is by default hidden for easier reading.
	To toggle on/off the raw code, click <a href="javascript:code_toggle()">here</a>.''')