EXPIRED_PASSPORT = """
<select id="ddls_0" data-index="0" onchange="ControloSelect(this)">
    <option value="0"> </option>
    <option value="1">Si</option>
    <option value="2">No</option>
</select>
"""

MARITAL_STATUS = """
<select id="ddls_2" data-index="2" onchange="ControloSelect(this)">
    <option value="0"> </option>
    <option value="13">Coniugato/a</option>
    <option value="14">Divorziato/a</option>
    <option value="15">Vedovo/a</option>
    <option value="16">Celibe/Nubile</option>
    <option value="17">Separato/a</option>
    <option value="18">Unito/a Civilmente</option>
    <option value="19">Separato/a da Un. Civ.</option>
    <option value="20">Divorziato/a da Un. Civ.</option>
    <option value="21">Vedovo/a da Un. Civ.</option>
</select>
"""

PARENTAL_RELATIONSHIP = """
<select id="TypeOfRelationDDL0" data-index="0">
    <option></option>
    <option value="2">Coniuge</option>
    <option value="11">Coniuge divorziato</option>
    <option value="1">Coniuge separato</option>
    <option value="9">Convivente</option>
    <option value="8">Figlio di altro coniuge</option>
    <option value="5">Figlio/a</option>
    <option value="7">Fratello/Sorella</option>
    <option value="3">Genero/Nuora</option>
    <option value="6">Genitore</option>
    <option value="12">Minore in affidamento</option>
    <option value="10">Nipote</option>
    <option value="4">Suocero/Suocera</option>
</select>
"""

MINOR_CHILDREN = """
<select id="ddls_1" data-index="1" onchange="ControloSelect(this)">
    <option value="0"> </option>
    <option value="11">Si</option>
    <option value="12">No</option>
</select>
"""

SINGLE_MULTIPLE_APPOINTMENT = """
<div id="typeofbooking">
    <input data-val="true" data-val-number="Il campo IDServizioConsolare deve essere un numero." data-val-required="The IDServizioConsolare field is required." id="IDServizioConsolare" name="IDServizioConsolare" type="hidden" value="2">
    <input data-val="true" data-val-number="Il campo IDServizioErogato deve essere un numero." data-val-required="The IDServizioErogato field is required." id="IDServizioErogato" name="IDServizioErogato" type="hidden" value="196">
    <label>Tipo Prenotazione</label>
    <select id="typeofbookingddl">
        <option value="1">Prenotazione Singola</option>
        <option value="2">Prenotazione Multipla</option>
    </select>
    <input data-val="true" data-val-number="Il campo IdTipoPrenotazione deve essere un numero." data-val-required="The IdTipoPrenotazione field is required." id="hiddenTipoPrenotazione" name="IdTipoPrenotazione" type="hidden" value="2">
    <input data-val="true" data-val-number="Il campo NumMaxAccompagnatori deve essere un numero." data-val-required="The NumMaxAccompagnatori field is required." id="hiddenNumMax" name="NumMaxAccompagnatori" type="hidden" value="5">
</div>
"""

AMOUNT_ADDITIONAL_PEOPLE_FOR_APPOINTMNET = """
<div id="numberOfCompanions" style="">
    <label>Numero richiedenti aggiuntivi</label>
    <select id="ddlnumberofcompanions">
        <option value="1"> 1 </option>
        <option value="2"> 2 </option>
        <option value="3"> 3 </option>
        <option value="4"> 4 </option>
        <option value="5"> 5 </option>
    </select>
    <input data-val="true" data-val-number="Il campo NumAccompagnatoriSelected deve essere un numero." data-val-required="The NumAccompagnatoriSelected field is required." id="numAccSelected" name="NumAccompagnatoriSelected" type="hidden" value="1">
</div>
"""
