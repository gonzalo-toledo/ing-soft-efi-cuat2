from django.contrib.auth.models import User
from pasajeros.models import Pasajero
from home.models import Nacionalidad
from vuelos.models import Vuelo, Aeropuerto
from rest_framework import serializers


#USUARIO
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
    )
    
    class Meta:
        model = User
        fields = [
            'pk',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'password'
        ]
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data) 
        if password:
            user.set_password(password)
        else:
            user.set_password(User.objects.make_random_password())
            #enviarle la contraseña por email
        user.save()
        #! Ver: al momento de crear un usuario, crearlo tambien como pasajero. Tener en cuenta que el modelo de pasajero tiene mas campos que el de usuario.
        #por ej en el proyecto anterior para crear un cliente podemos hacer:
        #Customer.objects.create (
        #   name=user.first_name,
        #   email=user.email,
        #   phone='123',
        # )
        return user
    
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        #Opcion 1
        for attr, value in validated_data.items(): 
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
        
        #Opcion 2: #!ESTA MAL PORQUE CREA UN NUEVO USUARIO
        # instance = User.objects.create(
        #     username=validated_data['username'],
        #     email=validated_data['email'],
        #     first_name=validated_data['first_name'],
        #     last_name=validated_data['last_name'],
        # )
        # instance.set_password(password)
        # instance.save()
        # return instance

        
#PASAJERO
class PasajeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pasajero
        fields = [
            'nombre',
            'apellido',
            'pasaporte',
            'fecha_nacimiento',
            'nacionalidad',
            'genero',
            'email',
            'telefono',
        ]


#USUARIO + PASAJERO
class RegistroSerializer(serializers.ModelSerializer):
    # Campos de User solo para input, no para output
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email_user = serializers.EmailField(write_only=True, source='email')

    # Campos de Pasajero
    pasaporte = serializers.CharField()
    fecha_nacimiento = serializers.DateField()
    nacionalidad = serializers.PrimaryKeyRelatedField(queryset=Nacionalidad.objects.all())
    genero = serializers.ChoiceField(choices=[('M','Masculino'),('F','Femenino'),('O','Otro')])
    telefono = serializers.CharField()

    class Meta:
        model = Pasajero
        fields = [
            'username','password','first_name','last_name','email_user',
        'pasaporte','fecha_nacimiento','nacionalidad','genero','telefono'
        ]

    def create(self, validated_data):
        # Extraer datos del usuario
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email', None)

        # Crear User
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        # Crear Pasajero
        pasajero = Pasajero.objects.create(
            usuario=user,
            nombre=first_name,
            apellido=last_name,
            email=email,
            **validated_data
        )
        return pasajero


#AEROPUERTO
class AeropuertoSerializer(serializers.Serializer): #con serializer a diferencia de ModelSerializer con que un modelo tenga el mismo atributo y no siempre el 100% se puede serializar
    id = serializers.IntegerField(read_only=True)
    iata = serializers.CharField(max_length=3)
    nombre = serializers.CharField(max_length=255)
    ciudad = serializers.CharField(max_length=100)
    provincia = serializers.CharField(max_length=100)
    pais = serializers.CharField(max_length=100)
    latitud = serializers.FloatField()
    longitud = serializers.FloatField()
    tipo = serializers.CharField(max_length=50)

    def create(self, validated_data):
        return Aeropuerto.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.iata = validated_data.get('iata', instance.iata)
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.ciudad = validated_data.get('ciudad', instance.ciudad)
        instance.provincia = validated_data.get('provincia', instance.provincia)
        instance.pais = validated_data.get('pais', instance.pais)
        instance.latitud = validated_data.get('latitud', instance.latitud)
        instance.longitud = validated_data.get('longitud', instance.longitud)
        instance.tipo = validated_data.get('tipo', instance.tipo)
        instance.save()
        return instance

class AeropuertoForVueloSerializer(serializers.Serializer):
    ciudad = serializers.CharField(max_length=100)

#VUELO
class VueloSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    avion = serializers.CharField(source='avion.modelo', read_only=True)  # Mostrar el modelo del avión
    origen = serializers.CharField(source='origen.ciudad', read_only=True)  # Mostrar la ciudad del aeropuerto de origen. Esta es una forma de hacerlo
    destino = AeropuertoForVueloSerializer(read_only=True)  # Mostrar solo la ciudad del aeropuerto de destino. Esta es la otra forma de hacerlo con otro serializer
    fecha_salida = serializers.DateTimeField()
    fecha_llegada = serializers.DateTimeField()
    duracion = serializers.DurationField(read_only=True)  # Duración del vuelo, solo lectura
    estado = serializers.CharField()
    precio_base = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_vuelos = serializers.SerializerMethodField()  # Campo calculado

    def get_total_vuelos(self, obj):
        return Vuelo.objects.count()