################################################################################
#                                                                              #
# Methods of defining and conjuring the elemental Forms. Forms are the         #
#  templates for all things, but they do not exist until they are instantiated.#
#  Actual forms can be found within the books of creation, located in the      #
#  books/ subdirectory.                                                        #
#                                                                              #
################################################################################
module Forms
	@@templates = {};

	def get_template(name)
		return @@templates[name];
	end

	def self.form(name, &block)
		name = name.downcase
		@@templates[name] = block;
	end

	def spawn(which)
		if (which.class == Array) 
			return spawn_multiple(which); 
		end	

		which = which.downcase
		return if @@templates[which].nil?
		noun = Noun.new;
		noun.instance_eval &@@templates[which]
		return noun;
	end

	def spawn_multiple(*things)
		out = [];
		things.each do |thing|
			out << spawn(thing)
		end
		return out;
	end

	def has_guts
		container << spawn(:heart, :blood)
	end
end
