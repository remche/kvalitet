/* mise à jour des champs ajax */

$(document).ready(function() {
	Dajaxice.fchach.update_next_user(Dajax.process, {'service':$('#id_team').find(':selected').val(),
							'fchach_id':$('div[name="fiche"]')[0].id });
});

$(document).on("change", "[name='team']", function() { 
					Dajaxice.compta.update_ligne(Dajax.process, {'service':$(this).find(':selected').val()});
                                        Dajaxice.fchach.update_next_user(Dajax.process, {'service':$(this).find(':selected').val()});
					}								
		);

$(document).on("change", "[name='batiment']", function() { 
					Dajaxice.compta.update_salle(Dajax.process, {'bat':$(this).find(':selected').val()})
					}								
		);

$(document).on("submit", "[id='fchach_form']", function( event ) {
				if (!$('#prod1').length){
					$('#noprod').modal();
					event.preventDefault();
				}
				else if($('#intitule')[0].value != ""){
					$('#prodleft').find("#forgotten")[0].textContent = $('#intitule')[0].value;
					$('#prodleft').modal();
					$('#prod_add').find("input").addClass("alert-error");
					$('#prod_add').find("select").addClass("alert-error");
					event.preventDefault();
				}
			}
);

$(document).on("click", "[id='prodleft-validate-btn']", function( event ) {
			$('#intitule')[0].value = "";
			$('#submit-id-submit').click();
			}
);
