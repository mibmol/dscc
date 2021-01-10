from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
	def create_user(
		self,
		email,
		first_name,
		last_name,
		password=None,
		has_provided_password=True,
		is_admin=False,
		is_gas_station_admin=False,
		cedula=None,
		address=None,
		phone_number=None,
	):
		if not email:
			raise ValueError("Users must have an email address")
		if not first_name:
			raise ValueError("Users must have a first name")
		if not last_name:
			raise ValueError("Users must have a last name")
		if not password:
			raise ValueError("Users must have a password")

		user = self.model(
			email=self.normalize_email(email),
			first_name=first_name,
			last_name=last_name,
			has_provided_password=has_provided_password,
			phone_number=phone_number,
			cedula=cedula,
			is_admin=is_admin,
			is_gas_station_admin=is_gas_station_admin,
			address=address,
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, first_name, last_name, password=None):
		user = self.create_user(
			email=email,
			first_name=first_name,
			last_name=last_name,
			password=password,
			has_provided_password=True,
		)
		user.is_superuser = True
		user.is_admin = True
		user.save(using=self._db)
		return user
