const foodAmount = '';

function main() {
    minLength.value="0";
    maxLength.value="20";
    menuSelector();
}

function menuToggler(shown, hidden1, hidden2) {
    shown.style.display = "block";
    hidden1.style.display = "none";
    hidden2.style.display = "none";
}

function menuSelector() {
    if(meal.selected) {
        menuToggler(mealMenu, symptomMenu, pottyMenu);
    } else if(potty.selected) {
        menuToggler(pottyMenu, mealMenu, symptomMenu);
    } else if(symptoms.selected) {
        menuToggler(symptomMenu, pottyMenu, mealMenu);
    }
}

function addFood() {
    // Find a <table> element with id="myTable":
    var table = document.getElementById("foodTable");

    // Create an empty <tr> element and add it to the 1st position of the table:
    var numFoods = table.rows.length - 1;
    var row = table.insertRow(numFoods);

    // Insert new cells (<td> elements) at the 1st and 2nd position of the "new" <tr> element:
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);

    // Add some text to the new cells:
    cell1.innerHTML = "<label>Food:<input type='text' size='20' maxlength='50' id='food" + (numFoods+1) + "' /></label>";
    cell2.innerHTML = "<label>Servings:<input type='text' size='3' maxlength='5' id='serving" + (numFoods+1) + "' /></label>";
}

function removeFood() {

    var table = document.getElementById("foodTable");

    if(table.rows.length === 2) {
        return;
    }

    try {
        
        var rowToDelete = table.rows.length - 2;

        table.deleteRow(rowToDelete);

    }catch(e) {
            alert(e);
    }
}

function submitMeal() {
    //FIXME add in function
}

function submitPoop() {
    //FIXME add in function
}

function submitSymptoms() {
    //FIXME add in function
}
// NUMBER OF FOODS IS STORED UNDER (foodTable.rows.length - 1)