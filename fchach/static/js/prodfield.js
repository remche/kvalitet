function isInt(val) {
	if (isNumber(val) && (parseFloat(val) == parseInt(val))){
		return true;
	} 
	else {
		return false;
	}
};

function isNumber(val) {
	if(!val || (typeof val != "string" || val.constructor != String)) {
		return(false);
	}
	return !isNaN(new Number(val));
};

function check_line(){
	$prix = $("#prix").val().replace(',','.');
	$qte = $("#quantite").val()

		if (isNumber($prix) && isInt($qte)){
			$("#sstotal").val(String($prix*$qte).replace('.',','));
			return true;
		}
		else{
			reset();
			return false;
		}

};

function reset(){
	$("#prod_add").find("input").map(function(){ $(this).val(""); });
	$("#mat_opt[value='']")[0].selected=true;
	$("#nom_opt[value='']")[0].selected=true;
	$("#quantite").val("1");
	$("#sstotal").val("0");
}

function recal_total(){
	total=0;
	$(".sstotal").each(function(){
		total += parseFloat($(this).val().replace(',','.'));
	});
	$('#total').val(String(total).replace('.',','));
};

$(document).on("click", "#add_button", function(){
	selected_mat = $(".mat_opt").filter(":selected")[0].value
	selected_nom = $(".nom_opt").filter(":selected")[0].value	
	selected_mat_label = $(".mat_opt").filter(":selected")[0].label
	selected_nom_label = $(".nom_opt").filter(":selected")[0].label
	if (check_line() && $("#intitule").val() && selected_mat && selected_nom){
		prod = "prod"+i;

		$("#total_line").before($("#prod_add")
			.clone()
			.attr("id",prod)
			);

		// on change l'id des champs
		$("#"+prod).find("td > .intitule").attr("id", "intitule-"+i);	
		$("#"+prod).find("td > .intitule").attr("name", "intitule-"+i);

		$("#"+prod).find("td > .nomenclature").attr("id", "nomenclature-"+i);	
		$("#"+prod).find("td > .nomenclature").attr("name", "nomenclature-"+i);	
		$("#"+prod).find("td > .nomenclature").attr("rel", "tooltip");	
		$("#"+prod).find("td > .nomenclature").attr("title", selected_nom_label);	
		$("#"+prod).find("td > .nomenclature").after("<input type='hidden' name='nomenclature-"+i+"' value='"+selected_nom+"' />");	
		$("#"+prod).find("td > .nomenclature").find("option[value="+selected_nom+"]")[0].selected = true;
		$("#"+prod).find("td > .nomenclature").find("option").map(function(){ $(this).attr("id", "nom_opt-"+i); });

		$("#"+prod).find("td > .matiere").attr("id", "matiere-"+i);	
		$("#"+prod).find("td > .matiere").attr("name", "matiere-"+i);	
		$("#"+prod).find("td > .matiere").attr("rel", "tooltip");	
		$("#"+prod).find("td > .matiere").attr("title", selected_mat_label);	
		$("#"+prod).find("td > .matiere").after("<input type='hidden' name='matiere-"+i+"' value='"+selected_mat+"' />");	
		$("#"+prod).find("td > .matiere").find("option[value="+selected_mat+"]")[0].selected = true;
		$("#"+prod).find("td > .matiere").find("option").map(function(){ $(this).attr("id", "mat_opt-"+i); });

		$("#"+prod).find("td > .prix").attr("id", "prix-"+i);	
		$("#"+prod).find("td > .prix").attr("name", "prix-"+i);	
		$("#"+prod).find("td > .qte").attr("id", "quantite-"+i);	
		$("#"+prod).find("td > .qte").attr("name", "quantite-"+i);	
		
		// readonly
		$("#"+prod).find("input").map(function(){ $(this).attr("readonly", "readonly"); });
		$("#"+prod).find("select").map(function(){ $(this).attr("disabled", "disabled"); });

		$("#"+prod).find("#add_button").children().remove();
		$("#"+prod).find("#add_button").append("<i class=icon-minus></i>");	
		$("#"+prod).find("#add_button").attr("class", "suppr");	
		$("#"+prod).find("#add_button").attr("id", "suppr-"+i);	

		reset();
		recal_total();

		i++;
	}
	else{
		$("#produits").before('<div class="alert alert-error"><a class="close" data-dismiss="alert" href="#">×</a><h4 class="alert-heading">Erreur</h4>Remplissez les champs correctement !</div>');
	}
});

$(document).on("click", ".suppr", function(){ $(this).parent().parent().remove(); recal_total(); });

$(document).on("change", ".prix,.qte", check_line);


/* Reponsive table */

$(document).ready(function() {
	  var switched = false;
	  var updateTables = function() {
	    if (($(window).width() < 980) && !switched ){
	      switched = true;
	      $("table.responsive").each(function(i, element) {
		minTable($(element));
	      });
	      return true;
	    }
	    else if (switched && ($(window).width() > 980)) {
	      switched = false;
	      $("table.responsive").each(function(i, element) {
		maxTable($(element));
	      });
	    }
	  };
	   
	  $(window).load(updateTables);
	  $(window).bind("resize", updateTables);
	   
		
	function minTable(table){
		table.find(".input-small").removeClass("input-small").addClass("input-mini butsmall");
		table.find(".input-normal").removeClass("input-normal").addClass("input-small butnormal");
		table.find("th#mat_xlab").text("XLAB");
		table.find("th#nomenclature").text("Nom.");
		}
		
	function maxTable(table) {
		table.find(".butnormal").removeClass("input-small butnormal").addClass("input-normal");
		table.find(".butsmall").removeClass("input-mini butsmall").addClass("input-small");
		table.find("th#mat_xlab").text("Matière XLAB");
		table.find("th#nomenclature").text("Nomenclature");
		}

});
