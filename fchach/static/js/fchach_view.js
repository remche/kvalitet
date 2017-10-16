/* Reponsive table */

$(document).ready(function() {
	  var switched = false;
	  var updateTables = function() {
	    if (($(window).width() < 534) && !switched ){
	      switched = true;
	      $("table.view-responsive").each(function(i, element) {
		minTable($(element));
	      });
	      return true;
	    }
	    else if (switched && ($(window).width() > 534)) {
	      switched = false;
	      $("table.view-responsive").each(function(i, element) {
		maxTable($(element));
	      });
	    }
	  };
	   
	  $(window).load(updateTables);
	  $(window).bind("resize", updateTables);
	   
		
	function minTable(table){
		table.find("th#mat_xlab").text("XLAB");
		table.find("th#nomenclature").text("Nom.");
		table.find("th#quantite").text("Qté");
		}
		
	function maxTable(table) {
		table.find("th#mat_xlab").text("Matière XLAB");
		table.find("th#nomenclature").text("Nomenclature");
		table.find("th#quantite").text("Quantite");
		}

});
