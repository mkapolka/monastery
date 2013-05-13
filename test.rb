class Brittle < Property
	description "is very brittle"
	types :physical
	def shatter(me, basher)
		say "#{me.name} shatters into pieces!", me, "see"
		shard = me.duplicate
		shard.name = "a shard of #{me.name}";
		shard.size-- if shard.size?
		shard.make :bladed
		shard.set_container me.parent;
		delete
	end

	def bash(me, basher)
		shatter me, basher
	end

	def jostle
		if (not me.parent.isRoom and me.parent.hard?)
			shatter me, basher
		end
	end
end

class Thick < Property
	description "is thick and viscous"
	types :physical
	also_make :holdable :if => :is_liquid

	held_action :slather do |me, caller, target|
		require_touch me, target
		say "You slather #{me.name} onto #{target.name}", me, :do;
		me.touch target
		me.merge_with target :types => [:chemical, :physical]
	end
end

class Troll_Blood < Property
	description "has regenerating properties"
	types :chemical
	def heartbeat(me, beater)
		if (beater.open?)
			say "#{beater.name}'s wounds close", beater, :see
			beater.unmake :open
		end
	end
end

class Lends_Properties < Property
	def describe(me)
		return "lends #{me.lends_properties} properties to its host."	
	end
	revealed_by :biology_knowledge

	attr_accessible :types

	def <<(types)
		types << types;
	end


	def lend_properties(from, to)
			
	end

	def entered_container(me, container)
		if not container return;
		if container.isRoom? return;
		if container.contents.find {|x| x.lends_properties == me.lends_properties} return;
		lend_properties(me, container)
	end
end
