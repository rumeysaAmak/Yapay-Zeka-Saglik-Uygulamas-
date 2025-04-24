const ogrenci={
    ad:"veli",
    soyad:"ali",
    ogrno:123
    
}

function yazdir({ad, soyad, ...kalanlar}){
    console.log(ad);
    console.log(soyad);
    console.log(kalanlar);
}

dizi7=[1,23,45,8];
function yazdır([ilk,ikinci,...kalanlar]){
    console.log(ilk);
    console.log(ikinci);
    console.log(kalanlar);
}

yazdır(dizi7);

yazdir(ogrenci);
console.log(ogrenci);

ogrenci.bolum="yazılım müh";

console.log(ogrenci);

console.log(ogrenci.ad); //ad'a ulaşmak için ogrenci.ad ile yani ogrenci objesinin içinde olduğu için doğrudan değil bu şekilde ulaşırız

//...(3 dot) operatörü

const ogrenci={
    ad:"veli",
    soyad:"ali",
    ogrno:123,
    bolum:"yazılım müh",
    adres:"bandırma"
    
}
console.log(ogrenci);

const{ad, soyad, ...kalanlar}=ogrenci;  //bu şekilde tanımlarsak direkt ad ve soyada doğrudan ulaşabiliriz.

console.log(ad);
console.log(soyad);
console.log(kalanlar.ogrno);
console.log(kalanlar.adres);
console.log(kalanlar.bolum);

//Spread

const dizi1=[1,2,3];
const dizi2=[2,...dizi1,5,6,7];

console.log(dizi2);
console.log(dizi2[3])


dizi3=[4,5,6];
dizi4=[7,9,1];

dizi5=[...dizi3,...dizi4];
console.log(dizi5);



//deep vs shallow copy

const a=[1,2];
const b=[...a];

console.log(b);

b.push(4);
b.push(5);
b.push(6);
b.push(7);

console.log(b);
console.log(a);




